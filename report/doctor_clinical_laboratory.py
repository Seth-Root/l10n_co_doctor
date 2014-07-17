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

class doctor_clinical_laboratory(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(doctor_clinical_laboratory, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'select_type': self.select_type,
        })

    def select_type(self, tipo_usuario):
        patient = self.pool.get('doctor.patient')
        tipo = dict(patient.fields_get(self.cr, self.uid, 'tipo_usuario').get('tipo_usuario').get('selection')).get(
            str(tipo_usuario))
        return tipo

report_sxw.report_sxw('report.doctor_clinical_laboratory', 'doctor.attentions',
                      'addons/l10n_co_doctor/report/doctor_clinical_laboratory.rml',
                      parser=doctor_clinical_laboratory)
        
        
        
        
