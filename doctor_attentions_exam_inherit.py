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


class doctor_attentions_exam_inherit(osv.osv):
	_name = "doctor.attentions.exam"
	_rec_name = 'attentiont_id'
	_columns = {
		'attentiont_id': fields.many2one('doctor.attentions', 'Attention'),
		'exam': fields.text('Exam', required=False),
		'exam_category': fields.many2one('doctor.exam.category', 'Exam category', required=False, ondelete='restrict'),	
	}


doctor_attentions_exam_inherit()