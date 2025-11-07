from app import db

epic_testcase = db.Table(
    'epic_testcase',
    db.Column('epic_id', db.Integer, db.ForeignKey('epic_hu.id')),
    db.Column('testcase_id', db.Integer, db.ForeignKey('test_case.id'))
)
