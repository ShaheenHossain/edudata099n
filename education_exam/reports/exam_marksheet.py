# -*- coding: utf-8 -*-

from datetime import datetime
import time, math
from odoo import fields, models,api
import pandas as pd
import numpy


class education_exam_marksheet(models.AbstractModel):
    _name = 'report.education_exam.report_exam_marksheet'

    def get_exams(self, objects):
        exams = []
        for exam in objects.exams:
           exams.extend(exam)

        return exams

    def get_students(self, objects):
        student = []
        if len(objects.student.id) >0:
            student_list = self.env['education.class.history'].search(
                [('student_id.id', '=', objects.student.id), ('academic_year_id.id', '=', objects.academic_year.id)])
            for stu in student_list:
                student.extend(stu)
        elif objects.section:
            student_list = self.env['education.class.history'].search([('class_id.id', '=', objects.section.id)])
            for stu in student_list:
                student.extend(stu)
        elif objects.level:
            student_list = self.env['education.class.history'].search([('level.id', '=', objects.level.id),
                                                                ('academic_year_id.id', '=',objects.academic_year.id)])
        for stu in student_list:
            student.extend(stu)

        return student

    def get_total_working_days(self,exams):
        working_days=0
        for exam in exams:
            working_days=working_days+exam.total_working_days
        return working_days


    @api.model
    def get_report_values(self, docids, data=None):
        docs = self.env['education.exam.result.wizard'].browse(docids)
        return {
            'doc_model': 'education.exam.results.new',
            'docs': docs,
            'time': time,
            'get_exams': self.get_exams,
            'get_results': self.get_results,
            'get_students': self.get_students,
            'get_total_working_days': self.get_total_working_days,

            'get_subjects': self.env['report.education_exam.report_dsblsc_marksheet'].get_subjects,
            'get_gradings':self.env['report.education_exam.report_dsblsc_marksheet'].get_gradings,
            'num2serial': self.env['report.education_exam.report_dsblsc_marksheet'].num2serial,
            'get_sections': self.env['report.education_exam.report_dsblsc_marksheet'].get_sections,
            'get_student_no': self.env['report.education_exam.report_dsblsc_marksheet'].get_student_no,
            'get_student_in_section': self.env['report.education_exam.report_dsblsc_marksheet'].get_student_in_section,
            'half_round_up': self.env['report.education_exam.report_dsblsc_marksheet'].half_round_up,
            'get_converted_report': self.env['report.education_exam.report_exam_evaluation'].get_converted_report,
        }
