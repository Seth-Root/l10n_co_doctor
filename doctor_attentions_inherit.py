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
import logging
_logger = logging.getLogger(__name__)
import openerp
import re
import codecs
from openerp.osv import fields, osv
from openerp.tools.translate import _


class doctor_attentions_co_inherit(osv.osv):
	'''
	Model to add on_change event which calculate BMI for patients.
	'''
	_description='Inherited Model to add on_change.'
	_name = "doctor.attentions"
	_inherit = "doctor.attentions"

	def onchange_calcularImc(self, cr, uid, ids, peso, talla, context=None):
		res = {'value':{}}
		imc = 0

		if not peso or not talla:
			imc = 0.00 
		try:
			imc = (peso / (( talla / 100.0  ) ** 2 ))	
		except:
			_logger.info("error en la función onchange_calcularImc [doctor_attentions_co_inherit.py]")	
		res['value']['body_mass_index'] = imc
		return res


	def onchange_interpretacionimc(self, cr, uid, ids, masa_corporal, context=None):
		res = {'value':{}}
		interpretacion = ''
		if masa_corporal:
			if masa_corporal < 16:
				interpretacion = 'Delgadez Severa'
			elif masa_corporal >= 16 and masa_corporal <= 16.99:
				interpretacion = 'Delgadez Moderada'
			elif masa_corporal >= 17 and masa_corporal <= 18.49:
				interpretacion = 'Delgadez Leve'
			elif masa_corporal >= 18.5 and masa_corporal <= 24.99:
				interpretacion = 'Normal'
			elif masa_corporal >= 16 and masa_corporal <= 16.99:
				interpretacion = 'Normal'
			elif masa_corporal >= 25 and masa_corporal <= 29.99:
				interpretacion = 'Preobeso'
			elif masa_corporal >= 30 and masa_corporal <= 34.99:
				interpretacion = 'Obesidad Leve'
			elif masa_corporal >= 35 and masa_corporal <= 39.99:
				interpretacion = 'Obesidad Media'
			elif masa_corporal >= 40:
				interpretacion = u'Obesidad Mórbida'
		res['value']['interpretacion_imc'] =  interpretacion
		return res
	

	_columns = {
		'interpretacion_imc' : fields.char(u'Interpretación', size=80, help=u'Interpretación de indice de masa corporal.', states={'closed': [('readonly', True)]}),
	}

	

doctor_attentions_co_inherit()