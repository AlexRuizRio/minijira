from app import db

testcase_testcycle = db.Table(
    'testcase_testcycle',
    db.Column('testcase_id', db.Integer, db.ForeignKey('test_case.id')),
    db.Column('testcycle_id', db.Integer, db.ForeignKey('test_cycle.id'))
)
