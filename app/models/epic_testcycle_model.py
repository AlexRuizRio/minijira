from app import db

epic_testcycle = db.Table(
    'epic_testcycle',
    db.Column('epic_id', db.Integer, db.ForeignKey('epic_hu.id')),
    db.Column('testcycle_id', db.Integer, db.ForeignKey('test_cycle.id'))
)
