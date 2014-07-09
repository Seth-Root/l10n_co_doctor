# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp
import re
import codecs
from openerp.osv import fields, osv
from openerp.tools.translate import _

import time
import pooler
from datetime import date, datetime, timedelta

import openerp.addons.decimal_precision as dp
from pytz import timezone
import pytz

from dateutil import parser
from dateutil import rrule
from dateutil.relativedelta import relativedelta

import math

from openerp import SUPERUSER_ID, tools

import sale
import netsvc
import doctor


class doctor_patient_co(osv.osv):
    _name = "doctor.patient"
    _inherit = 'doctor.patient'
    _description = "Information about the patient"
    _columns = {
        'tdoc': fields.selection((('RC','Registro civil'), ('TI','Tarjeta de identidad'),
                                  ('CC','Cédula de ciudadanía'), ('CE','Cédula de extranjería'), ('PA','Pasaporte'),
                                  ('NU','Número único de identificación'), ('AS','Adulto sin identificaciómn'), ('MS','Menor sin identificación')),
                                  'Tipo de Documento', required=True),
        'ref' :  fields.related ('patient', 'ref', type="char", relation="res.partner", string="Nº de identificación", required=True, readonly= True),
        'tipo_usuario':  fields.selection((('1','Contributivo'), ('2','Subsidiado'),
                                           ('3','Vinculado'), ('4','Particular'),
                                           ('5','Otro')), 'Tipo de usuario', required=True),
        'dpto' : fields.related ('patient', 'state_id', type="many2one", relation="res.country.state", string="Departamento", readonly= True),
        'mun' : fields.related ('patient', 'city_id', type="many2one", relation="res.country.state.city", string="Municipio", readonly= True),
        'direccion' : fields.related ('patient', 'street', type="char", relation="res.partner", string="Dirección", readonly= True),
        'zona':  fields.selection ((('U','Urbana'), ('R','Rural')), 'Zona de residencia', required=True),
        }

    def onchange_patient_data(self, cr, uid, ids, patient, photo, ref, dpto, mun, direccion, context=None):
        values = {}
        if not patient:
            return values
        patient_data = self.pool.get('res.partner').browse(cr, uid, patient, context=context)
        patient_img = patient_data.image_medium
        patient_ref = patient_data.ref
        patient_dpto = patient_data.state_id.id
        patient_mun = patient_data.city_id.id
        patient_direccion = patient_data.street
        values.update({
            'photo' : patient_img,
            'ref' : patient_ref,
            'dpto' : patient_dpto,
            'mun' : patient_mun,
            'direccion' : patient_direccion,
        })
        return {'value' : values}

    _defaults = {
        'tipo_usuario': '4',
        'zona' : 'U'
        }

# Función para evitar número de documento duplicado

    def _check_unique_ident(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids):
            ref_ids = self.search(cr, uid, [('ref', '=', record.ref), ('id', '<>', record.id)])
            if ref_ids:
                return False
        return True

    _constraints = [(_check_unique_ident, '¡Error! Número de intentificación ya existe en el sistema', ['ref']),
               ]

doctor_patient_co()

class doctor_appointment_co(osv.osv):
    _name = "doctor.appointment"
    _inherit = "doctor.appointment"
    _columns = {
        'ref' :  fields.related ('patient_id', 'ref', type="char", relation="doctor.patient", string="Nº de identificación", required=True, readonly= True),
        'tipo_usuario_id': fields.selection((('1','Contributivo'), ('2','Subsidiado'),
                                           ('3','Vinculado'), ('4','Particular'),
                                           ('5','Otro')), 'Tipo de usuario', states={'invoiced':[('readonly',True)]}),
        }

    def onchange_patient(self, cr, uid, ids, patient_id, insurer_id, tipo_usuario_id, ref, context=None):
        values = {}
        if not patient_id:
            return values
        patient = self.pool.get('doctor.patient').browse(cr, uid, patient_id, context=context)
        insurer_patient = patient.insurer.id
        tipo_usuario_patient = patient.tipo_usuario
        ref_patient = patient.ref
        values.update({
            'insurer_id' : insurer_patient,
            'tipo_usuario_id' : tipo_usuario_patient,
            'ref' : ref_patient,
        })
        return {'value' : values}

    def create_order(self, cr, uid, doctor_appointment, date, appointment_procedures, confirmed_flag, context={}):
        """
        Method that creates an order from given data.
        @param doctor_appointment: Appointment method get data from.
        @param date: Date of created order.
        @param appointment_procedures: Lines that will generate order lines.
        @confirmed_flag: Confirmed flag in agreement order line will be set to this value.
        """
        order_obj = self.pool.get('sale.order')
        order_line_obj = self.pool.get('sale.order.line')
        # Create order object
        order = {
            'date_order': date.strftime('%Y-%m-%d'),
            'origin': doctor_appointment.number,
            'partner_id': doctor_appointment.insurer_id.insurer.id,
            'patient_id': doctor_appointment.patient_id.id,
            'ref': doctor_appointment.ref,
            'tipo_usuario_id' : doctor_appointment.tipo_usuario_id,
            'state': 'draft',
        }
        # Get other order values from appointment partner
        order.update(sale.sale.sale_order.onchange_partner_id(order_obj, cr, uid, [], doctor_appointment.insurer_id.insurer.id)['value'])
        order['user_id'] = doctor_appointment.insurer_id.insurer.user_id.id
        order_id = order_obj.create(cr, uid, order, context=context)
        # Create order lines objects
        appointment_procedures_ids = []
        for procedures_id in appointment_procedures:
            order_line = {
                'order_id': order_id,
                'product_id': procedures_id.procedures_id.id,
                'product_uom_qty': procedures_id.quantity,
            }
            # get other order line values from appointment procedures line product
            order_line.update(sale.sale.sale_order_line.product_id_change(order_line_obj, cr, uid, [], order['pricelist_id'], \
                product=procedures_id.procedures_id.id, qty=procedures_id.quantity, partner_id=doctor_appointment.insurer_id.insurer.id, fiscal_position=order['fiscal_position'])['value'])
            # Put line taxes
            order_line['tax_id'] = [(6, 0, tuple(order_line['tax_id']))]
            # Put custom description
            if procedures_id.additional_description:
                order_line['name'] += " " + procedures_id.additional_description
            order_line_obj.create(cr, uid, order_line, context=context)
            appointment_procedures_ids.append(procedures_id.id)
        # Create order agreement record
        appointment_order = {
            'order_id': order_id,
        }
        self.pool.get('doctor.appointment').write(cr, uid, [doctor_appointment.id], appointment_order, context=context)

        return order_id

doctor_appointment_co()

class doctor_attentions_co(osv.osv):
    _name = "doctor.attentions"
    _inherit = 'doctor.attentions'
    _columns = {
        'finalidad_consulta':fields.selection([('01','Atención del parto -puerperio'),
                                                ('02','Atención del recién nacido'),
                                                ('03','Atención en planificación familiar'),
                                                ('04','Detección de alteraciones del crecimiento y desarrollo del menor de diez años'),
                                                ('05','Detección de alteración del desarrollo joven'),
                                                ('06','Detección de alteraciones del embarazo'),
                                                ('07','Detección de alteración del adulto'),
                                                ('08','Detección de alteración de agudeza visual'),
                                                ('09','Detección de enfermedad profesional'),
                                                ('10','No aplica'),
                                               ],'Finalidad de la consulta', states={'closed':[('readonly',True)]}),
        }

    _defaults = {
    'finalidad_consulta': '10',
    }

doctor_attentions_co()

class doctor_invoice_co (osv.osv):
    _inherit = "account.invoice"
    _name = "account.invoice"

    _columns = {
        'ref' :  fields.related ('patient_id', 'ref', type="char", relation="doctor.patient", string="Nº de identificación", required=True, readonly= True),
        'tipo_usuario_id': fields.selection((('1','Contributivo'), ('2','Subsidiado'),
                                           ('3','Vinculado'), ('4','Particular'),
                                           ('5','Otro')), 'Tipo de usuario'),
                 }

doctor_invoice_co()

class doctor_sales_order_co (osv.osv):
    _inherit = "sale.order"
    _name = "sale.order"

    _columns = {
        'ref' :  fields.related ('patient_id', 'ref', type="char", relation="doctor.patient", string="Nº de identificación", required=True, readonly= True),
        'tipo_usuario_id': fields.selection((('1','Contributivo'), ('2','Subsidiado'),
                                           ('3','Vinculado'), ('4','Particular'),
                                           ('5','Otro')), 'Tipo de usuario'),
                 }

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        """Prepare the dict of values to create the new invoice for a
           sales order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record order: sale.order record to invoice
           :param list(int) line: list of invoice line IDs that must be
                                  attached to the invoice
           :return: dict of value to create() the invoice
        """
        if context is None:
            context = {}
        journal_ids = self.pool.get('account.journal').search(cr, uid,
            [('type', '=', 'sale'), ('company_id', '=', order.company_id.id)],
            limit=1)
        if not journal_ids:
            raise osv.except_osv(_('Error!'),
                _('Please define sales journal for this company: "%s" (id:%d).') % (order.company_id.name, order.company_id.id))
        invoice_vals = {
            'name': order.client_order_ref or '',
            'origin': order.name,
            'type': 'out_invoice',
            'reference': order.client_order_ref or order.name,
            'account_id': order.partner_id.property_account_receivable.id,
            'partner_id': order.partner_invoice_id.id,
            'patient_id': order.patient_id.id,
            'ref': order.ref,
            'tipo_usuario_id': order.tipo_usuario_id,
            'journal_id': journal_ids[0],
            'invoice_line': [(6, 0, lines)],
            'currency_id': order.pricelist_id.currency_id.id,
            'amount_patient': order.amount_patient,
            'amount_partner':  order.amount_partner,
            'comment': order.note,
            'payment_term': order.payment_term and order.payment_term.id or False,
            'fiscal_position': order.fiscal_position.id or order.partner_id.property_account_position.id,
            'date_invoice': context.get('date_invoice', False),
            'company_id': order.company_id.id,
            'user_id': order.user_id and order.user_id.id or False
        }

        # Care for deprecated _inv_get() hook - FIXME: to be removed after 6.1
        invoice_vals.update(self._inv_get(cr, uid, order, context=context))
        return invoice_vals

doctor_sales_order_co()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
