from app import db


class Scores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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
    round = db.relationship('Rounds', backref=db.backref('scores', uselist=False))
    bow = db.relationship('BowTypes', backref=db.backref('scores', uselist=False))
    archer = db.relationship('Archers', backref=db.backref('scores', uselist=False))

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
        return '<Score id: {} score: {} hits: {} golds: {} date: {}>'.format(self.id, self.score, self.num_hits,
                                                                             self.num_golds, self.date)


class IndividualRecords(db.Model):
    __tablename__ = 'individual_records'

    archer_name = db.Column(db.String(255), primary_key=True)
    score = db.Column(db.Integer, primary_key=True)
    round_name = db.Column(db.String(255), primary_key=True)
    num_golds = db.Column(db.Integer, primary_key=True)
    round_type = db.Column(db.Enum('Imperial', 'Metric', 'WA Outdoors', 'WA Indoors', 'Clout', 'Indoors',
                                   name='ROUND_TYPE'), primary_key=True)
    bow_type = db.Column(db.String(255), primary_key=True)
    gender = db.Column(db.Enum('F', 'M', name='GENDER'), primary_key=True)
    category = db.Column(db.Enum('Novice', 'Experienced', name='CATEGORY'), primary_key=True)
    date = db.Column(db.Date, primary_key=False)

    def __init__(self, archer_name, score, round_name, num_golds, round_type, bow_type, gender, category, date):
        self.archer_name = archer_name
        self.round_name = round_name
        self.score = score
        self.num_golds = num_golds
        self.round_type = round_type
        self.bow_type = bow_type
        self.gender = gender
        self.category = category
        self.date = date


class Classifications(db.Model):
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
        return '<Classification round_id: {} bow_type: {} / {} {} {} {} {} {} {} {}>'.format(self.round_id,
                                                                                             self.bow_type,
                                                                                             self.class_a, self.class_b,
                                                                                             self.class_c, self.class_d,
                                                                                             self.class_e, self.class_f,
                                                                                             self.class_g, self.class_h)

    def get_class(self, score, round_type):
        if self.class_a is not None and score >= self.class_a:
            if 'Indoors' in round_type:
                return 'A'
            else:
                return 'GMB*'
        elif self.class_b is not None and score >= self.class_b:
            if 'Indoors' in round_type:
                return 'B'
            else:
                return 'MB*'
        elif self.class_c is not None and score >= self.class_c:
            if 'Indoors' in round_type:
                return 'C'
            else:
                return 'BM'
        elif self.class_d is not None and score >= self.class_d:
            if 'Indoors' in round_type:
                return 'D'
            else:
                return '1st'
        elif self.class_e is not None and score >= self.class_e:
            if 'Indoors' in round_type:
                return 'E'
            else:
                return '2nd'
        elif self.class_f is not None and score >= self.class_f:
            if 'Indoors' in round_type:
                return 'F'
            else:
                return '3rd'
        elif self.class_g is not None and score >= self.class_g:
            if 'Indoors' in round_type:
                return 'G'
            else:
                return None
        elif self.class_h is not None and score >= self.class_h:
            if 'Indoors' in round_type:
                return 'H'
            else:
                return None
        else:
            return None


class BowTypes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return '<BowType id: {} name {}>'.format(self.id, self.name)


class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return '<Event id: {} name {}>'.format(self.id, self.name)


class Rounds(db.Model):
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
        return '<Round name: {} id: {} type: {}>'.format(self.name, self.id, self.r_type)

    def is_outdoors(self):
        if 'Indoors' in self.r_type or self.r_type is 'Clout':
            return False
        else:
            return True


class Archers(db.Model):
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
        return "<Archer name: {} {} id: {} card_num: {}>".format(self.first_name, self.last_name, self.id,
                                                                 self.card_number)

    def get_name(self):
        return self.first_name + " " + self.last_name
