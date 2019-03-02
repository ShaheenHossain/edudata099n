# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError

class academicTranscript(models.Model):
    _name ='academic.transcript'
    _description='print academic transcript for selected exams'
    academic_year=fields.Many2one('education.academic.year',"Academic Year")
    level=fields.Many2one('education.class',"Level")
    exams=fields.Many2many('education.exam','transcript_id')
    specific_section = fields.Boolean('For a specific section')
    section=fields.Many2one('education.class.division')
    specific_student=fields.Boolean('For a specific Student')
    student=fields.Many2one('education.student','Student')
    state=fields.Selection([('draft','Draft'),('done','Done')],compute='calculate_state')
    @api.multi
    def calculate_state(self):
        results=self.env[('education.exam.results')].search([('academic_year','=',self.academic_year.id),('class_id','=','level')])
        for exam in self.exams:
            rec=results.search([('exam_id','=',exam.id)])
            for line in rec:
                if line.state!='done':
                    self.state='draft'
                    return True
        self.state='done'


    @api.multi
    @api.onchange('level', 'section')
    def get_student_domain(self):
        for rec in self:
            domain = []
            if rec.section:
                domain.append(('class_id','=',rec.section.id))
            else:
                domain.append(('class_id.class_id.id', '=', rec.level.id))

        return {'domain': {'student':domain}}
    @api.multi
    @api.onchange('specific_section')
    def onchange_specific_section(self):
        for rec in self:
            if rec.specific_section==False:
                rec.specific_student=False
                rec.section=False
    @api.multi
    def generate_results(self):
        for rec in self:
            for exam in self.exams:
                results_new_list=[]
                result_subject_line_list=[]
                result_paper_line_list=[]
                self.env['education.exam.results.new'].search([('exam_id', '=', exam.id)]).unlink()
                results = self.env['education.exam.results'].search([('exam_id', '=', exam.id)])
                for result in results:
                    result_data = {
                        "name": exam.name,
                        "exam_id": exam.id,
                        "student_id": result.student_id.id,
                        "result_id": result.id,
                        "academic_year": exam.academic_year.id,
                        "student_name": result.student_name,
                        "class_id": result.division_id.id,
                        "section_id": result.division_id.section_id.id
                    }
                    student_exam_obtained = 0
                    student_exam_passed = True

                    newResult = self.env['education.exam.results.new'].create(result_data)
                    results_new_list.append(newResult)
                    subject_list = {}

                    for paper in result.subject_line_ids:
                        present_subject_rules = self.env['exam.subject.pass.rules'].search(
                            [('exam_id', '=', exam.id), ('subject_id', '=', paper.subject_id.subject_id.id)])
                        if len(present_subject_rules) == 0:
                            values = {
                                'subject_id': paper.subject_id.subject_id.id,
                                'exam_id': exam.id,
                                'class_id': paper.subject_id.class_id.id
                            }
                            present_subject_rules = present_subject_rules.create(values)
                        present_paper_rules = self.env['exam.paper.pass.rules'].search(
                            [('subject_rule_id', '=', present_subject_rules.id),
                             ('paper_id', '=', paper.subject_id.id)])
                        if len(present_paper_rules) == 0:
                            paper_values = {
                                'subject_rule_id': present_subject_rules.id,
                                'paper_id': paper.subject_id.id,
                                'tut_mark': paper.subject_id.tut_mark,
                                'subj_mark': paper.subject_id.subj_mark,
                                'obj_mark': paper.subject_id.obj_mark,
                                'prac_mark': paper.subject_id.prac_mark
                            }
                            present_paper_rules = present_paper_rules.create(paper_values)

                        subjectId = paper.subject_id.subject_id
                        if subjectId not in subject_list:
                            subject_data = {
                                "subject_id": subjectId.id,
                                "result_id": newResult.id,
                                "pass_rule_id": present_subject_rules.id
                            }
                            newSubject = self.env["results.subject.line.new"].create(subject_data)
                            result_subject_line_list.append(newSubject)
                            subject_list[subjectId] = newSubject
                        else:
                            newSubject = subject_list[subjectId]
                        paper_data = {
                            "subject_line": newSubject.id,
                            "paper_id": paper.subject_id.id,
                            "pass_rule_id": present_paper_rules.id,
                            "tut_obt": paper.tut_obt,
                            "subj_obt": paper.subj_obt,
                            "obj_obt": paper.obj_obt,
                            "prac_obt": paper.prac_obt,
                            "tut_pr": paper.tut_pr,  # pr for present/Absent data
                            "subj_pr": paper.subj_pr,
                            "obj_pr": paper.obj_pr,
                            "prac_pr": paper.prac_pr,
                        }
                        new_paper = self.env["results.paper.line"].create(paper_data)
                        result_paper_line_list.append(new_paper)
            self.calculate_subject_rules(subject_list,exam)
            self.calculate_result_paper_lines(result_paper_line_list)
            self.calculate_result_subject_lines(result_subject_line_list)
            self.get_result_type_count(exam)
            self.calculate_subjects_results(exam)
    @api.multi
    def calculate_subject_rules(self,subject_list,exam):
        for subjects in subject_list:
            subjectRules= self.env['exam.subject.pass.rules'].search(
                    [('exam_id', '=', exam.id), ('subject_id', '=', subjects.id)])
            for line in subjectRules:
                for paper_rule in line.paper_ids:
                    paper_rule.name = paper_rule.paper_id.paper
                    paper_rule.paper_marks = paper_rule.tut_mark + paper_rule.subj_mark + paper_rule.obj_mark + paper_rule.prac_mark
                line.academic_year = line.exam_id.academic_year.id
                line.name = line.subject_id.name + " for " + line.class_id.name + "-" + line.academic_year.name
                subject_full_marks = 0
                subjective_mark = 0
                objective_mark = 0
                tutorial_mark = 0
                practical_mark = 0
                for paper in line.paper_ids:
                    subject_full_marks = subject_full_marks + paper.paper_marks
                    subjective_mark = subjective_mark + paper.subj_mark
                    objective_mark = objective_mark + paper.obj_mark
                    tutorial_mark = tutorial_mark + paper.tut_mark
                    practical_mark = practical_mark + paper.prac_mark
                line.subject_marks = subject_full_marks
                line.prac_mark = practical_mark
                line.obj_mark = objective_mark
                line.subj_mark = subjective_mark
                line.tut_mark = tutorial_mark

    @api.multi
    def calculate_subjects_results(self, exam):
        student_lines = self.env['education.exam.results.new'].search([('exam_id', '=', exam.id)])
        for student in student_lines:
            student_compulsory_obtained = 0
            compulsory_gp = 0
            compulsory_count = 0
            student_optional_obtained = 0
            optional_gp = 0
            optional_count = 0
            general_count = 0
            student_extra_obtained = 0
            extra_count = 0
            extra_gp = 0

            student_passed = True

            for subject in student.subject_line:
                paper_count = 0
                passed = True
                optional = False
                extra = False
                for paper in subject.paper_ids:
                    if paper.paper_id in student.student_history.optional_subjects:
                        optional_ = True
                    elif paper.paper_id.evaluation_type == 'extra':
                        extra = True
                    paper_count = paper_count + 1
                    if paper.paper_id.tut_mark > 0:
                        student.show_tut = True
                    if paper.paper_id.subj_mark > 0:
                        student.show_subj = True
                    if paper.paper_id.obj_mark > 0:
                        student.show_obj = True
                    if paper.paper_id.prac_mark > 0:
                        student.show_prac = True
                if extra == True:
                    subject.extra_for = student.id
                    student.extra_row_count = student.extra_row_count + paper_count
                    student.extra_count = student.extra_count + 1
                    student.extra_obtained = student.extra_obtained + subject.mark_scored
                    student.extra_gp = student.extra_gp + subject.grade_point
                    if passed == False:
                        student.extra_fail_count = student.extra_fail_count + 1
                elif optional == True:
                    subject.optional_for = student.id
                    student.optional_count = student.optional_count + 1
                    student.optional_row_count = student.optional_row_count + paper_count
                    student.optional_obtained = student.optional_obtained + subject.mark_scored
                    student.optional_gp = student.optional_gp + subject.grade_point
                    if passed == False:
                        student.optional_fail_count = student.optional_fail_count + 1
                else:
                    subject.general_for = student.id
                    student.general_count = student.general_count + 1
                    student.general_row_count = student.general_row_count + paper_count
                    student.general_obtained = student.general_obtained + subject.mark_scored
                    student.general_gp = student.general_gp + subject.grade_point
                    if passed == False:
                        student.general_fail_count = student.general_fail_count + 1
                if paper_count > 1:
                    student.show_paper = True
        ddd = student.general_subject_line

    @api.multi
    def calculate_result_paper_lines(self,result_paper_lines):
        for rec in result_paper_lines:
            passFail = True
            if rec.pass_rule_id.tut_pass > rec.tut_obt:
                passFail = False
            elif rec.pass_rule_id.subj_pass > rec.subj_obt:
                passFail = False
            elif rec.pass_rule_id.obj_pass > rec.obj_obt:
                passFail = False
            elif rec.pass_rule_id.prac_pass > rec.prac_obt:
                passFail = False
            elif rec.pass_rule_id.tut_mark > 0:
                if rec.tut_pr == False:
                    passFail = False
            elif rec.pass_rule_id.subj_mark > 0:
                if rec.subj_pr == False:
                    passFail = False
            elif rec.pass_rule_id.obj_mark > 0:
                if rec.obj_pr == False:
                    passFail = False
            elif rec.pass_rule_id.prac_mark > 0:
                if rec.prac_pr == False:
                    passFail = False
            paper_obtained = 0
            if rec.pass_rule_id.tut_mark > 0:
                paper_obtained = paper_obtained + rec.tut_obt
            if rec.pass_rule_id.subj_mark > 0:
                paper_obtained = paper_obtained + rec.subj_obt
            if rec.pass_rule_id.obj_mark > 0:
                paper_obtained = paper_obtained + rec.obj_obt
            if rec.pass_rule_id.prac_mark > 0:
                paper_obtained = paper_obtained + rec.prac_obt
            rec.paper_obt = paper_obtained
            rec.passed = passFail
            if passFail == True:
                rec.gp = self.env['education.result.grading'].get_grade_point(rec.pass_rule_id.paper_marks,
                                                                              rec.paper_obt)
                rec.lg = self.env['education.result.grading'].get_letter_grade(rec.pass_rule_id.paper_marks,
                                                                               rec.paper_obt)
            else:
                rec.gp = 0
                rec.lg = 'F'

    @api.multi
    def calculate_result_subject_lines(self,result_subject_lines):
        for rec in result_subject_lines:
            practical_obt = 0
            subjective_obt = 0
            objective_obt = 0
            tutorial_obt = 0
            practical_mark = 0
            subjective_mark = 0
            objective_mark = 0
            tutorial_mark = 0
            passed = True
            for line in rec.paper_ids:
                practical_obt = practical_obt + line.prac_obt
                subjective_obt = subjective_obt + line.subj_obt
                objective_obt = objective_obt + line.obj_obt
                tutorial_obt = tutorial_obt + line.tut_obt
                practical_mark = practical_mark+line.pass_rule_id.tut_mark
                subjective_mark = subjective_mark+line.pass_rule_id.subj_mark
                objective_mark = objective_mark+line.pass_rule_id.obj_mark
                tutorial_mark = tutorial_mark+line.pass_rule_id.tut_mark
                if line.passed == False:
                    passed = False
            rec.tut_obt = tutorial_obt
            rec.prac_obt = practical_obt
            rec.subj_obt = subjective_obt
            rec.obj_obt = objective_obt
            rec.tut_mark=tutorial_mark
            rec.prac_mark=practical_mark
            rec.subj_mark=subjective_mark
            rec.obj_mark=objective_mark

            if passed == False:
                passed = False
            elif rec.pass_rule_id.tut_pass > rec.tut_obt:
                passed = False
            elif rec.pass_rule_id.subj_pass > rec.subj_obt:
                passed = False
            elif rec.pass_rule_id.obj_pass > rec.obj_obt:
                passed = False
            elif rec.pass_rule_id.prac_pass > rec.prac_obt:
                passed = False

            rec.mark_scored = 0
            if rec.pass_rule_id.tut_mark > 0:
                rec.mark_scored = rec.mark_scored + rec.tut_obt
            if rec.pass_rule_id.subj_mark > 0:
                rec.mark_scored = rec.mark_scored + rec.subj_obt
            if rec.pass_rule_id.obj_mark > 0:
                rec.mark_scored = rec.mark_scored + rec.obj_obt
            if rec.pass_rule_id.prac_mark > 0:
                rec.mark_scored = rec.mark_scored + rec.prac_obt
            if passed == True:
                rec.grade_point = rec.env['education.result.grading'].get_grade_point(
                    rec.pass_rule_id.total_mark,
                    rec.mark_scored)
                rec.letter_grade = rec.env['education.result.grading'].get_letter_grade(
                    rec.pass_rule_id.total_mark,
                    rec.mark_scored)
            else:
                rec.grade_point = 0
                rec.letter_grade = 'F'

    @api.multi
    def get_result_type_count(self,exam):
        result_lines=self.env['education.exam.results.new'].search([('exam_id','=',exam.id)])
        for rec in result_lines:
            res_type_count = 0
            if rec.show_tut == True:
                res_type_count = res_type_count + 1
            if rec.show_subj == True:
                res_type_count = res_type_count + 1
            if rec.show_obj == True:
                res_type_count = res_type_count + 1
            if rec.show_prac == True:
                res_type_count = res_type_count + 1
            rec.result_type_count = res_type_count




