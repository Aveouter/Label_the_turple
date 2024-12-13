from libs.shape import Shape

class Relationship(object):


    def __init__(self, sub, obj, relation_id , predicate = None):
        self.predicate = predicate
        self.sub = sub
        self.obj = obj
        self.rel_id = relation_id



    def show_rel(self):
        txt = None
        if self.predicate:
            if isinstance(self.sub , Shape) and isinstance(self.obj , Shape):
                txt = "<" + self.sub.label + "," + self.predicate + "," + self.obj.label+">";

        return txt