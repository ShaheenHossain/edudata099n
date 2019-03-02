# -*- coding: utf-8 -*-


from odoo import models, fields, api


class resultGradingSystem(models.Model):
    _name = 'education.result.grading'
    _rec_name = 'result'

    min_per = fields.Integer('Minimum Percentage', required=True)
    max_per = fields.Integer('Maximum Percentage', required=True)
    result = fields.Char('Result to Display', required=True)
    score = fields.Float('Score')

    @api.multi
    def get_grade_point(self,ful_mark,obtained):
        grade_point=0
        if ful_mark>0:
            per_obtained = ((obtained * 100) / ful_mark)
            grades = self.search([['id', '>', '0']])
            for gr in grades:
                if gr.min_per <= per_obtained and gr.max_per >= per_obtained:
                    grade_point = gr.score
        return grade_point
    @api.multi
    def get_letter_grade(self,ful_mark,obtained):
        letter_grade='F'
        if ful_mark>0:
            per_obtained = ((obtained * 100) / ful_mark)
            grades = self.search([['id', '>', '0']])
            for gr in grades:
                if gr.min_per <= per_obtained and gr.max_per >= per_obtained:
                    letter_grade = gr.result
        return letter_grade
