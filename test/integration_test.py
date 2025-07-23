import sys
import os
import unittest
import json
from unittest.mock import patch  # Import mock explicitly
from utils import read_json
from hospital_management import HospitalManager

class TestIntegration(unittest.TestCase):

    def setUp(self):
        self.manager = HospitalManager()
        # Clean the test environment
        for f in ["patients.json", "doctors.json", "beds.json"]:
            with open(f, "w") as file:
                json.dump([], file)

    def test_add_patient_and_assign_bed(self):
        self.manager.add_patient("John", 35, "male", "yellow")
        self.manager.add_bed("General", "A")

        patients = read_json("patients.json")
        beds = read_json("beds.json")
        pid = patients[0]["id"]
        bid = beds[0]["id"]

        self.manager.assign_bed_to_patient(pid, bid)
    
        # Re-read the data
        updated_beds = read_json("beds.json")
        self.assertEqual(updated_beds[0]["patientId"], pid)
        self.assertEqual(updated_beds[0]["status"], "occupied")

    def test_add_doctor_and_assign_to_patient(self):
        self.manager.add_patient("Jane", 28, "female", "red")
        self.manager.add_doctor("Dr. Smith", 45, "male", "Cardiology")

        patients = read_json("patients.json")
        doctors = read_json("doctors.json")
        pid = patients[0]["id"]
        did = doctors[0]["id"]

        self.manager.assign_doctor_to_patient(pid, did)

        updated_patients = read_json("patients.json")
        self.assertEqual(updated_patients[0]["doctorId"], did)

    def test_discharge_patient(self):
        self.manager.add_patient("Alice", 30, "female", "yellow")
        self.manager.add_bed("ICU", "B")

        patients = read_json("patients.json")
        beds = read_json("beds.json")
        pid = patients[0]["id"]
        bid = beds[0]["id"]

        self.manager.assign_bed_to_patient(pid, bid)
        self.manager.discharge_patient(pid)

        updated_patients = read_json("patients.json")
        updated_beds = read_json("beds.json")

        self.assertTrue(updated_patients[0]["isDeleted"])
        self.assertIsNone(updated_beds[0]["patientId"])
        self.assertEqual(updated_beds[0]["status"].lower(), "vacant")

    def test_update_patient_priority(self):
        self.manager.add_patient("Bob", 40, "male", "green")
        self.manager.add_bed("Special", "C")

        patients = read_json("patients.json")
        beds = read_json("beds.json")
        pid = patients[0]["id"]
        bid = beds[0]["id"]

        self.manager.assign_bed_to_patient(pid, bid)
        self.manager.update_patient_priority(pid, "red")

        updated_patients = read_json("patients.json")
        updated_beds = read_json("beds.json")

        self.assertEqual(updated_patients[0]["priority"].lower(), "red")
        self.assertEqual(updated_beds[0]["priority"].lower(), "red")

    def tearDown(self):
        for f in ["patients.json", "doctors.json", "beds.json", "patients_backup.json", "beds_backup.json", "doctors_backup.json"]:
            if os.path.exists(f):
                os.remove(f)

if __name__ == '__main__':
    unittest.main()