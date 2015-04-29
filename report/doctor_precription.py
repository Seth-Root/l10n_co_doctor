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
###############################################################################

import time
from openerp.report import report_sxw
from openerp import pooler

class doctor_precription(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(doctor_precription, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'select_type': self.select_type,
            'select_type_action': self.select_type_action,
            'select_type_unit': self.select_type_unit,
            'select_type_period': self.select_type_period,
        })

    def select_type(self, tipo_usuario):
        context = {}
        context.update({'lang' : self.pool.get('res.users').browse(self.cr, self.uid, self.uid, context=context).lang})
        patient = self.pool.get('doctor.patient')
        tipo = dict(patient.fields_get(self.cr, self.uid, 'tipo_usuario',context=context).get('tipo_usuario').get('selection')).get(
            str(tipo_usuario))
        return tipo

    def select_type_action(self, action):
        context = {}
        context.update({'lang' : self.pool.get('res.users').browse(self.cr, self.uid, self.uid, context=context).lang})
        presciption = self.pool.get('doctor.prescription')
        tipo = dict(presciption.fields_get(self.cr, self.uid, 'action_id',context=context).get('action_id').get('selection')).get(
            str(action))
        return tipo

    def select_type_unit(self, unit):
        context = {}
        context.update({'lang' : self.pool.get('res.users').browse(self.cr, self.uid, self.uid, context=context).lang})
        prescription = self.pool.get('doctor.prescription')
        tipo = dict(prescription.fields_get(self.cr, self.uid, 'frequency_unit_n',context=context).get('frequency_unit_n').get('selection')).get(
            str(unit))
        return tipo

    def select_type_period(self, period):
        context = {}
        context.update({'lang' : self.pool.get('res.users').browse(self.cr, self.uid, self.uid, context=context).lang})
        prescription = self.pool.get('doctor.prescription')
        tipo = dict(prescription.fields_get(self.cr, self.uid, 'dutation_period_n',context=context).get('dutation_period_n').get('selection')).get(
            str(period))
        return tipo



report_sxw.report_sxw('report.doctor_precription', 'doctor.attentions',
                      'addons/l10n_co_doctor/report/doctor_prescription.rml',
                      parser=doctor_precription)
        
        
        
        