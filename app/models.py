from app import db


class Score(db.Model):
    __tablename__ = 'scores'

    id = db.column(db.Integer, primary_key=True)
    archer_id = db.Column(db.Integer, db.ForeignKey('archers.id'), nullable=False)
    round_id = db.Column(db.Integer, db.ForeignKey('rounds.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    bow_type = db.Column(db.Integer, db.ForeignKey('bow_types.id'), nullable=False)
    category = db.Column(db.Enum('Novice', 'Experienced', name='CATEGORY'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    num_hits = db.Column(db.Integer, nullable=False)
    num_golds = db.Column(db.Integer, nullable=False)
    num_xs = db.Column(db.Integer, nullable=True)
    date = db.Column(db.Date, nullable=False)

    def __init__(self, id, archer_id, round_id, event_id, bow_type, category, score, num_hits, num_golds, num_xs, date):
        self.id = id
        self.archer_id = archer_id
        self.round_id = round_id
        self.event_id = event_id
        self.bow_type = bow_type
        self.category = category
        self.score = score
        self.num_hits = num_hits
        self.num_golds = num_golds
        self.num_xs = num_xs
        self.date = date

    def __repr__(self):
        return '<Score id: %d score: %d hits: %d golds: %d date: %s>'.format(self.id, self.score, self.num_hits,
                                                                             self.num_golds, self.date)


class Classification(db.Model):
    __tablename__ = 'classifications'

    round_id = db.Column(db.Integer, db.ForeignKey('rounds.id'), primary_key=True)
    bow_type = db.Column(db.Integer, db.ForeignKey('bow_types.id'), primary_key=True)
    gender = db.Column(db.Enum('F', 'M', name='GENDER'), primary_key=True)
    class_a = db.Column(db.Integer, nullable=True)
    class_b = db.Column(db.Integer, nullable=True)
    class_c = db.Column(db.Integer, nullable=True)
    class_d = db.Column(db.Integer, nullable=True)
    class_e = db.Column(db.Integer, nullable=True)
    class_f = db.Column(db.Integer, nullable=True)
    class_g = db.Column(db.Integer, nullable=True)
    class_h = db.Column(db.Integer, nullable=True)

    def __init__(self, round_id, bow_type, gender, class_a, class_b, class_c, class_d, class_e, class_f, class_g,
                 class_h):
        self.round_id = round_id
        self.bow_type = bow_type
        self.gender = gender
        self.class_a = class_a
        self.class_b = class_b
        self.class_c = class_c
        self.class_d = class_d
        self.class_e = class_e
        self.class_f = class_f
        self.class_g = class_g
        self.class_h = class_h

    def __repr__(self):
        return '<Classification round_id: %d bow_type: %d>'.format(self.round_id, self.bow_type)


class BowType(db.Model):
    __tablename__ = 'bow_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return '<BowType id: %d name %s>'.format(self.id, self.name)


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return '<Event id: %d name %s>'.format(self.id, self.name)


class Round(db.Model):
    __tablename__ = 'rounds'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    r_type = db.Column('type', db.Enum('Imperial', 'Metric', 'WA Outdoors', 'WA Indoors', 'Clout', 'Indoors',
                                       name='ROUND_TYPE'), nullable=False)
    max_hits = db.Column(db.Integer, nullable=False)
    max_score = db.Column(db.Integer, nullable=False)
    scoring_zones = db.Column(db.Enum('5', '10', name='SCORING_ZONES'), nullable=False)

    def __init__(self, id, name, r_type, max_hits, max_score, scoring_zones):
        self.id = id
        self.name = name
        self.r_type = r_type
        self.max_hits = max_hits
        self.max_score = max_score
        self.scoring_zones = scoring_zones

    def __repr__(self):
        return '<Round name: %s id: %s type: %s>'.format(self.name, self.id, self.r_type)


class Archer(db.Model):
    __tablename__ = 'archers'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.Enum('F', 'M', name='GENDER'), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    card_number = db.Column(db.String(7), nullable=True)
    agb_card = db.Column(db.String(10), nullable=True)

    def __init__(self, id, first_name, last_name, gender, email, card_number, agb_card):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.email = email
        self.card_number = card_number
        self.agb_card = agb_card

    def __repr__(self):
        return "<Archer name: %s %s id: %d card_num: %d>".format(self.first_name, self.last_name, self.id,
                                                                 self.card_number)