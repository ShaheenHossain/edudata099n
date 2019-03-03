
from odoo import models, fields, api


class EducationExamResultsNew(models.Model):
    _name = 'education.exam.results.new'
    _description = "this table contains student Wise exam results"

    name = fields.Char(string='Name' ,related="result_id.name" )
    result_id=fields.Many2one("education.exam.results","result_id",ondelete="cascade")             #relation to the result table
    exam_id = fields.Many2one('education.exam', string='Exam',ondelete="cascade")
    class_id = fields.Many2one('education.class.division', string='Class')
    division_id = fields.Many2one('education.class.division', string='Division')
    section_id = fields.Many2one('education.class.section', string='Section')
    student_id = fields.Many2one('education.student', string='Student')
    student_history=fields.Many2one('education.class.history',"Student History",compute='get_student_history',store="True")
    student_name = fields.Char(string='Student')
    subject_line = fields.One2many('results.subject.line.new', 'result_id', string='Subjects')
    general_subject_line = fields.One2many('results.subject.line.new', 'general_for', string='General Subjects')
    optional_subject_line = fields.One2many('results.subject.line.new', 'optional_for', string='optional Subjects')
    extra_subject_line = fields.One2many('results.subject.line.new', 'extra_for', string='extra Subjects')
    academic_year = fields.Many2one('education.academic.year', string='Academic Year')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())
    total_pass_mark = fields.Float(string='Total Pass Mark')
    total_max_mark = fields.Float(string='Total Max Mark')

    general_full_mark=fields.Float("Full Mark")
    general_obtained=fields.Integer("General_total")
    general_count=fields.Integer("General Subject Count")
    general_row_count=fields.Integer("General Paper Count")
    general_fail_count = fields.Integer("Genera Fail")
    general_gp=fields.Float('general GP')
    general_gpa = fields.Float("general GPA")

    extra_Full=fields.Integer("extra Full mark")
    extra_obtained=fields.Integer("extra Obtained")
    extra_count=fields.Integer("extra Count")
    extra_row_count=fields.Integer("extra Row Count")
    extra_fail_count=fields.Integer("Extra Fail")
    extra_gp=fields.Float('Extra GP')
    extra_gpa = fields.Float("Extra GPA")

    optional_Full=fields.Integer("Optional full")
    optional_obtained=fields.Integer("Optional obtained")
    optional_count=fields.Integer("optional Count")
    optional_row_count=fields.Integer("optional Row Count")
    optional_fail_count=fields.Integer("optional Fail Count")
    optional_gp=fields.Float('Optional LG')
    optional_gpa = fields.Char("Optional GPA")
    optional_gpa_above_2 = fields.Float("Optional GPA Above 2")
    optional_obtained_above_40_perc=fields.Integer("Aditional marks from optionals")

    net_obtained = fields.Integer(string='Total Marks Scored')
    net_pass = fields.Boolean(string='Overall Pass/Fail')
    net_lg=fields.Char("Letter Grade")
    net_gp = fields.Float("Net GP")
    net_gpa=fields.Float("GPA")

    working_days=fields.Integer('Working Days')
    attendance=fields.Integer('Attendance')
    percentage_of_attendance=fields.Float("Percentage of Attendance")
    behavior=fields.Char("Behavior")
    sports=fields.Char("Sports Program")
    uniform=fields.Char("Uniform")
    cultural=fields.Char("Caltural Activities")
    state=fields.Selection([('draft',"Draft"),('done',"Done")],"State",default='draft')

    show_tut=fields.Boolean('Show Tutorial')
    show_subj=fields.Boolean('Show Subj')
    show_obj=fields.Boolean('Show Obj')
    show_prac=fields.Boolean('Show Prac')
    show_paper=fields.Boolean('Show Papers')
    result_type_count=fields.Integer("result type Count")

    @api.depends('general_gp','general_count')
    def get_general_gpa(self):
        for rec in self:
            if rec.general_count>0:
                if rec.general_fail_count<1:
                    if rec.extra_fail_count < 1:
                        rec.general_gpa=rec.general_gp/rec.general_count
            if rec.optional_count>0:
                if rec.optional_fail_count<1:
                    rec.optional_gpa=rec.optional_gp/rec.optional_count
                    if rec.optional_gpa>2:
                        rec.optional_gpa_above_2=rec.optional_gpa-2

                    if rec.optional_gpa>0:
                        optional_40_perc=rec.optional_Full*100/40
                        rec.optional_obtained_above_40_perc=rec.optional_obtained-optional_40_perc
            rec.net_obtained=rec.general_obtained+rec.optional_obtained_above_40_perc
            if rec.general_count>0:
                rec.net_gpa=rec.general_gpa+(rec.optional_gpa_above_2/rec.general_count)
            if rec.extra_count>0:
                if rec.extra_fail_count<1:
                    rec.extra_gpa=rec.extra_gp/rec.extra_count

    @api.depends('student_id','class_id')
    def get_student_history(self):
        for rec in self:
            history = self.env['education.class.history'].search(
                [('student_id', '=', rec.student_id.id), ('academic_year_id', '=', rec.academic_year.id)])
            rec.student_history=history.id

    @api.multi
    def calculate_result(self,exams):
        for exam in exams:
            self.env['education.exam.results.new'].search([('exam_id','=',exam.id)]).unlink()
            results = self.env['education.exam.results'].search([('exam_id','=',exam.id)])
            for result in results:
                result_data={
                    "name": exam.name,
                    "exam_id": exam.id,
                    "student_id": result.student_id.id,
                    "result_id": result.id,
                    "academic_year": exam.academic_year.id,
                    "student_name": result.student_name,
                    "class_id": result.class_id.id
                }
                student_exam_obtained=0
                student_exam_passed=True

                newResult=self.create(result_data)
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
                            'tut_mark':paper.subject_id.tut_mark,
                            'subj_mark':paper.subject_id.subj_mark,
                            'obj_mark':paper.subject_id.obj_mark,
                            'prac_mark':paper.subject_id.prac_mark
                        }
                        present_paper_rules = present_paper_rules.create(paper_values)
                        present_paper_rules.calculate_paper_pass_rule_fields

                    subjectId=paper.subject_id.subject_id
                    if subjectId not in subject_list:
                        subject_data={
                            "subject_id":subjectId.id,
                            "result_id":newResult.id,
                            "pass_rule_id":present_subject_rules.id
                        }
                        newSubject=self.env["results.subject.line.new"].create(subject_data)
                        subject_list[subjectId] = newSubject
                    else:
                        newSubject=subject_list[subjectId]
                    paper_data={
                        "subject_line": newSubject.id,
                        "paper_id": paper.subject_id.id,
                        "pass_rule_id": present_paper_rules.id,
                        "tut_obt": paper.tut_obt,
                        "subj_obt": paper.subj_obt,
                        "obj_obt": paper.obj_obt,
                        "prac_obt": paper.prac_obt,
                        "tut_pr": paper.tut_pr,  #pr for present/Absent data
                        "subj_pr": paper.subj_pr,
                        "obj_pr": paper.obj_pr,
                        "prac_pr": paper.prac_pr,
                        }
                    new_paper=self.env["results.paper.line"].create(paper_data)
                    new_paper.get_name
                newResult.get_result_type_count



class ResultsSubjectLineNew(models.Model):
    _name = 'results.subject.line.new'
    name = fields.Char(string='Name',related='subject_id.name')
    result_id = fields.Many2one('education.exam.results.new', string='Result Id', ondelete="cascade")
    general_for = fields.Many2one('education.exam.results.new', string='General', ondelete="cascade")
    optional_for = fields.Many2one('education.exam.results.new', string='optional', ondelete="cascade")
    extra_for = fields.Many2one('education.exam.results.new', string='Extra', ondelete="cascade")
    pass_rule_id=fields.Many2one('exam.subject.pass.rules',"Pass Rule",ondelete="cascade")
    subject_id = fields.Many2one('education.subject', string='Subject')
    paper_ids=fields.One2many('results.paper.line','subject_line','Papers')

    tut_mark=fields.Float("Tutorial",related="pass_rule_id.tut_mark")
    subj_mark=fields.Float("Subjective",related="pass_rule_id.subj_mark")
    obj_mark=fields.Float("Objective",related="pass_rule_id.obj_mark")
    prac_mark=fields.Float("Practical",related="pass_rule_id.prac_mark")

    tut_obt = fields.Integer(string='Tutorial')
    subj_obt = fields.Integer(string='Subjective')
    obj_obt = fields.Integer(string='Objective')
    prac_obt = fields.Integer(string='Practical')
    mark_scored = fields.Float(string='Mark Scored')
    paper_count=fields.Integer('Paper Count')
    letter_grade=fields.Char('Grade')
    grade_point=fields.Float('GP')
    subject_highest = fields.Float(string='Max Mark')
    pass_mark = fields.Float(string='Pass Mark')
    pass_or_fail = fields.Boolean(string='Pass/Fail')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())

class result_paper_line(models.Model):
    _name = 'results.paper.line'
    name=fields.Char("Name")
    pass_rule_id=fields.Many2one('exam.paper.pass.rules',ondelete="cascade")
    subject_line=fields.Many2one('results.subject.line.new',ondelete="cascade")
    paper_id=fields.Many2one("education.syllabus","Paper")
    tut_obt = fields.Float(string='Tutorial')
    subj_obt = fields.Float(string='Subjective')
    obj_obt = fields.Float(string='Objective')
    prac_obt = fields.Float(string='Practical')
    prac_pr = fields.Boolean(string='P',default=True)
    subj_pr = fields.Boolean(string='P',default=True)
    obj_pr = fields.Boolean(string='P',default=True)
    tut_pr = fields.Boolean(string='P',default=True)
    paper_obt=fields.Float("Paper obtained Mark")
    passed=fields.Boolean("Passed?" )
    lg=fields.Char("letter Grade")
    gp=fields.Float("grade Point")

    @api.onchange('tut_obt','subj_obt','obj_obt','prac_obt')
    def calculate_paper_obtained(self):
        self.paper_obt=self.tut_obt+self.prac_obt+self.subj_obt+self.obj_obt