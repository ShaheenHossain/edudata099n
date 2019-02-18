
from odoo import models, fields, api


class EducationExamResultsNew(models.Model):
    _name = 'education.exam.results.new'

    name = fields.Char(string='Name' ,related="result_id.name" , store=True)
    result_id=fields.Many2one("education.exam.results","result_id")             #relation to the result table
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
    general_count=fields.Integer("General Count")
    general_fail_count = fields.Integer("Genera Fail")
    general_gp=fields.Float('general LG')
    general_lg=fields.Char("general GP")
    general_gpa = fields.Char("general GPA")

    extra_obtained=fields.Integer("extra total")
    extra_count=fields.Integer("extra Count")
    extra_fail_count=fields.Integer("Extra Fail")
    extra_lg=fields.Float('Extra LG')
    extra_gp=fields.Char("Extra GP")
    extra_gpa = fields.Char("Extra GPA")

    optional_obtained=fields.Integer("Optional total")
    optional_count=fields.Integer("optional Count")
    optional_fail_count=fields.Integer("optional Fail Count")
    optional_lg=fields.Float('Optional LG')
    optional_gp=fields.Char("Optional GP")
    optional_gpa = fields.Char("Optional GPA")

    net_total_mark = fields.Integer(string='Total Marks Scored')
    net_pass = fields.Boolean(string='Overall Pass/Fail')
    net_lg=fields.Char("Letter Grade")
    net_gp = fields.Char("Net GP")
    net_gpa=fields.Float("GPA")

    working_days=fields.Integer('Working Days')
    attendance=fields.Integer('Attendance')
    percentage_of_attendance=fields.Float("Percentage of Attendance")
    behavior=fields.Char("Behavior")
    sports=fields.Char("Sports Program")
    uniform=fields.Char("Uniform")
    cultural=fields.Char("Caltural Activities")
    state=fields.Selection([('draft',"Draft"),('done',"Done")],"State",default='draft')

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
                    subjectId=paper.subject_id.subject_id
                    if subjectId.id not in subject_list:
                        subject_list[subjectId]=newResult
                        subject_data={
                            "subject_id":subjectId.id,
                            "result_id":newResult.id,

                        }
                        newSubject=self.env["results.subject.line.new"].create(subject_data)
                    else:
                        newSubject=subject_list[subjectId]
                    paper_data={
                        "subject_line": newSubject.id,
                        "paper_id": paper.subject_id.id,
                        "tut_obt": paper.tut_mark,
                        "subj_obt": paper.subj_mark,
                        "obj_obt": paper.obj_mark,
                        "prac_obt": paper.prac_mark,
                        "tut_pr": paper.tut_pr,  #pr for present/Absent data
                        "subj_pr": paper.subj_pr,
                        "obj_pr": paper.obj_pr,
                        "prac_pr": paper.prac_pr,
                    }
                    new_paper=self.env["results.paper.line"].create(paper_data)
                    ful_mark=0
                    Passed=True
                    obtained=0

                    if newResult.class_id.id==11: # here 11 is for class SSC
                        if new_paper.paper_id.prac_mark>0:
                            if new_paper.prac_pr==True:  #check Present
                                Passed = False
                            if new_paper.paper_id.prac_pass>new_paper.prac_mark:
                                Passed=False
                            obtained=obtained+new_paper.prac_mark
                            ful_mark=ful_mark+new_paper.paper_id.prac_mark
                            newSubject.prac_mark=newSubject.prac_mark+new_paper.paper_id.prac_mark
                            newSubject.prac_ob=newSubject.prac_ob+new_paper.prac_mark


                        if new_paper.paper_id.subj_mark>0:
                            if new_paper.subj_pr==True:  #check Present
                                Passed = False
                            if new_paper.paper_id.subj_pass>new_paper.subj_obt:
                                Passed=False
                            obtained=obtained+new_paper.subj_obt
                            ful_mark = ful_mark + new_paper.paper_id.subj_mark
                            newSubject.subj_mark = newSubject.subj_mark + new_paper.paper_id.subj_mark
                            newSubject.subj_ob = newSubject.subj_ob + new_paper.subj_obt
                        if new_paper.paper_id.obj_mark>0:
                            if new_paper.obj_pr==True:  #check Present
                                Passed = False
                            if new_paper.paper_id.obj_pass>new_paper.obj_obt:
                                Passed=False
                            obtained=obtained+new_paper.obj_obt
                            ful_mark = ful_mark + new_paper.paper_id.obj_mark
                            newSubject.obj_mark = newSubject.obj_mark + new_paper.paper_id.obj_mark
                            newSubject.obj_ob = newSubject.obj_ob + new_paper.obj_obt
                        if new_paper.paper_id.tut_mark>0:
                            if new_paper.tut_pr==True:  #check Present
                                Passed = False
                            if new_paper.paper_id.tut_pass>new_paper.tut_obt:
                                Passed=False
                            obtained=obtained+new_paper.tut_obt
                            ful_mark = ful_mark + new_paper.paper_id.tut_mark
                            newSubject.tut_mark = newSubject.tut_mark + new_paper.paper_id.tut_mark
                            newSubject.tut_ob = newSubject.tut_ob + new_paper.tut_obt
                        if new_paper.paper_id.pass_mark > obtained:
                            Passed = False
                        new_paper.passed=Passed
                        new_paper.paper_obt=obtained
                        new_paper.paper_full=ful_mark
                        if Passed==True:
                            new_paper.gp=self.env['education.result.grading'].get_grade_point(new_paper.paper_id.total_mark,obtained)
                            grades = self.env['education.result.grading'].search([('score', '<=', new_paper.gp)],
                                                                                 limit=1, order='score DESC')
                            new_paper.lg= grades.result
                        else:
                            new_paper.gp=0
                            new_paper.lg="F"
            self.calculate_subjects_results(exam)
                # TODO edit students results Here
    @api.multi
    def calculate_subjects_results(self,exam):
        student_lines=self.search([('exam_id','=',exam.id)])
        for student in student_lines:
            student_compulsory_obtained=0
            compulsory_gp=0
            compulsory_count=0
            student_optional_obtained=0
            optional_gp=0
            optional_count=0

            student_extra_obtained=0
            extra_count=0
            extra_gp=0

            student_passed=True


            for subject in student.subject_line:
                paper_count=0
                passed=True
                fullmark=0
                optional=False
                extra=False
                obtained=0
                for paper in subject.paper_ids:
                    fullmark = fullmark + paper.paper_id.total_mark
                    obtained=obtained+paper.paper_id.paper_obtained
                    if paper.paper_id in student.student_history.optional_subjects:
                        optional_=True
                    elif paper.paper_id.evaluation_type=='extra':
                        extra=True

                    paper_count=paper_count+1
                    if paper.passed==False:
                        passed=False
                subject.max_mark=fullmark
                subject.mark_scored=obtained
               ########################################################
               #Start here to impliment the logic for all class pass fail rules
                #### rules for class SSC ,ID==11
                if student.student_history.class_id.class_id.id==11:  # 11 is id of class ssc
                    #### Rules for English , ID==2
                    if subject.subject_id.id==2: # rules for English
                        if subject.mark_scored<33 : #TODO implement subject.subject_id.pass_mark
                            passed=False
                    #### Rules for ICT , ID==6
                    elif subject.subject_id.id==6: # rules for English
                        if subject.mark_scored<17:  #TODO implement subject.subject_id.pass_mark
                            passed=False
                    else:
                        if subject.mark_scored<subject.pass_mark:
                            passed=False

                #end of pass fail rules
                ###############################################################





                if passed==True:
                    subject.grade_point=self.env['education.result.grading'].get_grade_point(fullmark,subject.mark_scored)
                    grades = self.env['education.result.grading'].search([('score', '<=', subject.grade_point)],
                                                                         limit=1, order='score DESC')
                    subject.letter_grade = grades.result
                else:
                    subject.grade_point=0
                    subject.letter_grade="F"
                if extra==True:
                    student.extra_count=student.extra_count+1
                    student.extra_obtained=student.extra_obtained+subject.mark_scored
                    student.extra_lg=student.extra_lg+fullmark
                    if passed==False:
                        student.extra_fail_count=student.extra_fail_count +1
                    student.extra_gp=student.extra_gp+subject.grade_point
                elif optional==True:
                    student.optional_count = student.optional_count + 1
                    student.optional_obtained = student.optional_obtained + subject.mark_scored
                    student.optional_lg = student.optional_lg + fullmark
                    if passed==False:
                        student.optional_fail_count = student.optional_fail_count + 1
                    student.optional_gp = student.optional_gp + subject.grade_point
                else:
                    student.general_count = student.general_count + 1
                    student.general_obtained = student.general_obtained + subject.mark_scored
                    if passed==False:
                        student.general_fail_count = student.general_fail_count + 1
                    student.general_gp = student.general_gp + subject.grade_point

class ResultsSubjectLineNew(models.Model):
    _name = 'results.subject.line.new'
    name = fields.Char(string='Name')
    result_id = fields.Many2one('education.exam.results.new', string='Result Id', ondelete="cascade")
    subject_id = fields.Many2one('education.subject', string='Subject')
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
    max_mark = fields.Integer(string='Max Mark')
    pass_mark = fields.Integer(string='Pass Mark')
    mark_scored = fields.Integer(string='Mark Scored')
    pass_or_fail = fields.Boolean(string='Pass/Fail')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())

class result_paper_line(models.Model):
    _name = 'results.paper.line'
    subject_line=fields.Many2one('results.subject.line.new','Subject_id',ondelete="cascade")
    paper_id=fields.Many2one("education.syllabus","Paper")
    tut_obt = fields.Integer(string='Tutorial')
    subj_obt = fields.Integer(string='Subjective')
    obj_obt = fields.Integer(string='Objective')
    prac_obt = fields.Integer(string='Practical')
    prac_pr = fields.Boolean(string='P',default=False)
    subj_pr = fields.Boolean(string='P',default=False)
    obj_pr = fields.Boolean(string='P',default=False)
    tut_pr = fields.Boolean(string='P',default=False)
    paper_obt=fields.Integer("Paper obtained Mark")
    passed=fields.Boolean("Passed?")
    lg=fields.Char("letter Grade")
    gp=fields.Float("grade Point")
    # @api.onchange('gp')
    # @api.multi
    # def get_letter_grade(self):
    #     for rec in self:
    #         if rec.passed!=True:
    #             rec.lg="F"
    #         else:
    #             leter_grade=self.env['education.result.grading'].search([('score', '<=', grade_point)], limit=1, order='score DESC')
    #             rec.lg= leter_grade.result