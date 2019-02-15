
from odoo import models, fields, api


class EducationExamResultsNew(models.Model):
    _name = 'education.exam.results.new'

    name = fields.Char(string='Name' ,related="result_id.name" , store=True)
    result_id=fields.Many2one("education.exam.results","result_id")
    exam_id = fields.Many2one('education.exam', string='Exam')
    class_id = fields.Many2one('education.class', string='Class')
    division_id = fields.Many2one('education.class.division', string='Division')
    section_id = fields.Many2one('education.class.section', string='Section',related="student_history.section",store=True)
    student_id = fields.Many2one('education.student', string='Student')
    student_history=fields.Many2one('education.class.history',"Student History",compute="get_student_history",store=True)
    student_name = fields.Char(string='Student')
    subject_line = fields.One2many('results.subject.line.new', 'result_id', string='Subjects')
    academic_year = fields.Many2one('education.academic.year', string='Academic Year',
                                    related='division_id.academic_year_id', store=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())
    total_pass_mark = fields.Integer(string='Total Pass Mark')
    total_max_mark = fields.Integer(string='Total Max Mark')
    general_obtained=fields.Integer("General_total")
    optional_obtained=fields.Integer("Optional total")
    extra_obtained=fields.Integer("extra total")
    all_obtained=fields.Integer("Total Obtained")
    general_count=fields.Integer("General Count")
    optional_count=fields.Integer("optional Count")
    extra_count=fields.Integer("extra Count")
    general_gp=fields.Char("general GP")
    optional_gp=fields.Char("Optional GP")
    extra_gp=fields.Char("Extra GP")
    general_gpa = fields.Char("general GPA")
    optional_gpa = fields.Char("Optional GPA")
    extra_gpa = fields.Char("Extra GPA")
    general_lg=fields.Float('general LG')
    optional_lg=fields.Float('Optional LG')
    extra_lg=fields.Float('Extra LG')
    working_days=fields.Integer('Working Days')
    attendance=fields.Integer('Attendance')
    percentage_of_attendance=fields.Float("Percentage of Attendance")
    behavior=fields.Char("Behavior")
    sports=fields.Char("Sports Program")
    uniform=fields.Char("Uniform")
    cultural=fields.Char("Caltural Activities")
    overall_pass = fields.Boolean(string='Overall Pass/Fail')
    no_of_general_subject=fields.Integer("No of General Subjects")
    state=fields.Selection([('draft',"Draft"),('done',"Done")],"State",default='draft')

    total_mark_scored = fields.Integer(string='Total Marks Scored')
    gpa=fields.Float("GPA")
    LG=fields.Char("Letter Grade")
    gpa_optional=fields.Float("GPA (Op)")
    gpa_net=fields.Float("GPA (Net)")
    lg_op=fields.Char("LG (Op)")
    lg_net=fields.Char("LG (Net)")
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
                }
                newResult=self.create(result_data)
                subject_list = {}
                for paper in result.subject_line_ids:
                    if paper.subject_id.subject_id.id not in subject_list:
                        subject_list[paper.subject_id.subject_id.id]=[newResult.id]
                        subject_data={
                            "subject_id":paper.subject_id.subject_id.id,
                            "result_id":newResult.id,

                        }
                        newSubject=self.env["results.subject.line.new"].create(subject_data)
                    paper_data={
                        "subject_line": subject_list[paper.subject_id.subject_id.id][0],
                        "tut_mark": paper.tut_mark,
                        "subj_mark": paper.subj_mark,
                        "obj_mark": paper.obj_mark,
                        "prac_mark": paper.prac_mark,
                        # "tut_ob": paper.tut_ob,
                        # "subj_ob": paper.subj_ob,
                        # "obj_ob": paper.obj_ob,
                        # "prac_ob": paper.prac_ob,
                        "tut_pr": paper.tut_pr,  #pr for present/Absent data
                        "subj_pr": paper.subj_pr,
                        "obj_pr": paper.obj_pr,
                        "prac_pr": paper.prac_pr,
                    }
                    new_paper=self.env["results.paper.line"].create(paper_data)



class ResultsSubjectLineNew(models.Model):
    _name = 'results.subject.line.new'
    name = fields.Char(string='Name')
    paper_ids=fields.One2many('results.paper.line','subject_line','Papers')
    tut_mark = fields.Integer(string='Tutorial')
    subj_mark = fields.Integer(string='Subjective')
    obj_mark = fields.Integer(string='Objective')
    prac_mark = fields.Integer(string='Practical')
    tut_ob = fields.Integer(string='Tutorial')
    subj_ob = fields.Integer(string='Subjective')
    obj_ob = fields.Integer(string='Objective')
    prac_ob = fields.Integer(string='Practical')
    letter_grade=fields.Char('Grade')
    grade_point=fields.Float('GP')
    subject_id = fields.Many2one('education.subject', string='Subject')
    max_mark = fields.Integer(string='Max Mark')
    pass_mark = fields.Integer(string='Pass Mark')
    mark_scored = fields.Integer(string='Mark Scored')
    pass_or_fail = fields.Boolean(string='Pass/Fail')
    result_id = fields.Many2one('education.exam.results.new', string='Result Id')
    exam_id = fields.Many2one('education.exam', string='Exam')
    class_id = fields.Many2one('education.class', string='Class')
    division_id = fields.Many2one('education.class.division', string='Division')
    student_id = fields.Many2one('education.student', string='Student')
    student_name = fields.Char(string='Student')
    academic_year = fields.Many2one('education.academic.year', string='Academic Year',
                                    related='division_id.academic_year_id', store=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())

class result_paper_line(models.Model):
    _name = 'results.paper.line'
    subject_line=fields.Many2one('result.subject.line.new','Subject_id')
    tut_mark = fields.Integer(string='Tutorial')
    subj_mark = fields.Integer(string='Subjective')
    obj_mark = fields.Integer(string='Objective')
    prac_mark = fields.Integer(string='Practical')
    prac_pr = fields.Boolean(string='P',default=False)
    subj_pr = fields.Boolean(string='P',default=False)
    obj_pr = fields.Boolean(string='P',default=False)
    tut_pr = fields.Boolean(string='P',default=False)