class Person:
    def __init__(self, id, name, age, gender):
        self._id = str(id)
        self._is_deleted = False
        self.name = name
        self.age = int(age)
        self.gender = gender.capitalize()

    @property
    def id(self):
        return self._id

    @property
    def is_deleted(self):
        return self._is_deleted

    def mark_deleted(self):
        self._is_deleted = True

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "isDeleted": self.is_deleted
        }

class Patient(Person):
    def __init__(self, id, name, age, gender, priority="yellow"):
        super().__init__(id, name, age, gender)
        self.priority = priority.capitalize()
        self.present_medication = []
        self.past_medication = []
        self.doctor_id = None
        self.bed_id = None

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "priority": self.priority,
            "present_medication": self.present_medication,
            "past_medication": self.past_medication,
            "doctorId": self.doctor_id,
            "bedId": self.bed_id
        })
        return base_dict

class Doctor(Person):
    def __init__(self, id, name, age, gender, specialization):
        super().__init__(id, name, age, gender)
        self.specialization = specialization

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "specialization": self.specialization
        })
        return base_dict

class Bed:
    def __init__(self, id, bed_type="General", ward="A"):
        self._id = str(id)
        self._is_deleted = False
        self.bed_type = bed_type
        self.ward = ward
        self.patient_id = None
        self.priority = None
        self.status = "Vacant"

    @property
    def id(self):
        return self._id

    @property
    def is_deleted(self):
        return self._is_deleted

    def mark_deleted(self):
        self._is_deleted = True

    def assign(self, patient_id, priority):
        self.patient_id = patient_id
        self.priority = priority
        self.status = "Occupied"

    def vacate(self):
        self.patient_id = None
        self.priority = None
        self.status = "Vacant"

    def to_dict(self):
        return {
            "id": self.id,
            "ward": self.ward,
            "bed_type": self.bed_type,
            "patientId": self.patient_id,
            "priority": self.priority,
            "status": self.status,
            "isDeleted": self.is_deleted
        }
