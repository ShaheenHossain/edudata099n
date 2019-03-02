# -*- coding: utf-8 -*-


from odoo import models, fields, api


class test_test(models.Model):
    _name = "education.test"
    name=fields.Char("dddd")
    tut_obt=fields.Float('tut')
    obt=fields.Float('obt',compute='get_name',store="True")
    ddd=fields.Float("ddd")
    @api.depends('tut_obt')
    def get_name(self):
        self.ddd=self.tut_obt*99
        self.obt=self.tut_obt
class test_test2(models.Model):
    _name = "education.test2"
    name=fields.Char("dddd")
    tut_obt=fields.Float('tut')
    obt=fields.Float('obt',compute='get_name',store="True")
    ddd=fields.Float("ddd")

    @api.multi
    def get_name(self):
        data={
            'tut_obt':self.tut_obt
        }
        self.env['education.test'].create(data)