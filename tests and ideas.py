


if False or (True):
    print("yes")

#class Picture:
#
#    def __init__(self, color, shape):
#        self.color = color
#        self.shape = shape
#
#    def __str__(self):
#        return f"Picture shape is {self.shape} and its color is {self.color}"
#
#    def __eq__(self, other):
#        if isinstance(other, Picture):
#            if self.color == other.color and self.shape == other.shape:
#                return True
#        return False
#
#
#pic1 = Picture("green", "triangle")
#pic2 = Picture("yellow", "square")
#pic3 = Picture("yellow", "square")
#
#print(pic3 == pic2)














#class Meta(type):
#    def __new__(self, class_name, bases, attrs):
#
#        a = {}
#        for name, val in attrs.items():
#            if name.startswith("__"):
#                a[name] = val
#            else:
#                a[name.upper()] = val
#
#        return type(class_name, bases, a)
#
#
#class Dog(metaclass=Meta):
#    x = 5
#    y = 8
#
#    def hello(self):
#        print("hi")
#
#d = Dog()
#
#print(d.HELLO())  # works
#
#print(d.hello())  # attr error



#class Person:
#    def __init__(self, first_name, last_name, age):
#        self.first_name = first_name
#        self.last_name = last_name
#        self.age = age
#
#    def __eq__(self, other):
#        if isinstance(other, Person):
#            return self.age == other.age
#
#        return False
#
#
#john = Person('John', 'Doe', 25)
#jane = Person('Jane', 'Doe', 25)
#mary = Person('Mary', 'Doe', 27)
#
#print(john == jane)  # True
#print(john == mary)  # False
#
#
#john = Person('John', 'Doe', 25)
#print(john == 20)  # False



