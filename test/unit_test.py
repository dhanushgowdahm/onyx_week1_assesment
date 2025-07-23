import unittest
from unittest.mock import patch, MagicMock
from hospital_management import HospitalManager

class TestHospitalManager(unittest.TestCase):
    def setUp(self):
        self.hm = HospitalManager()

    @patch("hospital_management.write_json")
    @patch("hospital_management.read_json", return_value=[])
    @patch("hospital_management.Patient")
    def test_add_patient(self, mock_patient, mock_read_json, mock_write_json):
        mock_patient.return_value.to_dict.return_value = {"id": "P1"}
        self.hm.add_patient("Alice", 28, "female", "red")
        mock_write_json.assert_called()

    @patch("hospital_management.write_json")
    @patch("hospital_management.read_json", return_value=[])
    @patch("hospital_management.Doctor")
    def test_add_doctor(self, mock_doctor, mock_read_json, mock_write_json):
        mock_doctor.return_value.to_dict.return_value = {"id": "D1"}
        self.hm.add_doctor("Bob", 40, "male", "Cardiology")
        mock_write_json.assert_called()

    @patch("hospital_management.write_json")
    @patch("hospital_management.read_json", return_value=[])
    @patch("hospital_management.Bed")
    def test_add_bed(self, mock_bed, mock_read_json, mock_write_json):
        mock_bed.return_value.to_dict.return_value = {"id": "B1"}
        self.hm.add_bed("ICU", "B")
        mock_write_json.assert_called()

    @patch("hospital_management.write_json")
    @patch("hospital_management.read_json")
    def test_assign_bed_to_patient(self, mock_read_json, mock_write_json):
        mock_read_json.side_effect = [
            [{"id": "P1"}],  # patients
            [{"id": "B1"}]   # beds
        ]
        self.hm.assign_bed_to_patient("P1", "B1")
        mock_write_json.assert_called()

    @patch("hospital_management.write_json")
    @patch("hospital_management.read_json")
    def test_assign_doctor_to_patient(self, mock_read_json, mock_write_json):
        mock_read_json.side_effect = [
            [{"id": "P1"}],  # patients
            [{"id": "D1"}]   # doctors
        ]
        self.hm.assign_doctor_to_patient("P1", "D1")
        mock_write_json.assert_called()

    @patch("hospital_management.write_json")
    @patch("hospital_management.read_json")
    def test_discharge_patient(self, mock_read_json, mock_write_json):
        mock_read_json.side_effect = [
            [{"id": "P1", "isDeleted": False}],  # patients
            [{"id": "B1", "patientId": "P1"}]    # beds
        ]
        self.hm.discharge_patient("P1")
        mock_write_json.assert_called()

    @patch("hospital_management.write_json")
    @patch("hospital_management.read_json")
    def test_update_patient_priority(self, mock_read_json, mock_write_json):
        mock_read_json.side_effect = [
            [{"id": "P1", "isDeleted": False}],  # patients
            [{"id": "B1", "patientId": "P1", "isDeleted": False}]  # beds
        ]
        self.hm.update_patient_priority("P1", "red")
        mock_write_json.assert_called()

    @patch("hospital_management.write_json")
    @patch("hospital_management.read_json")
    def test_change_bed_for_patient(self, mock_read_json, mock_write_json):
        mock_read_json.side_effect = [
            [{"id": "P1", "bedId": "B1", "priority": "red", "isDeleted": False}],  # patients
            [
                {"id": "B1", "patientId": "P1", "priority": "red", "status": "occupied", "isDeleted": False},
                {"id": "B2", "patientId": None, "priority": None, "status": "vacant", "isDeleted": False}
            ]  # beds
        ]
        self.hm.change_bed_for_patient("P1", "B2")
        mock_write_json.assert_called()

    @patch("hospital_management.write_json")
    @patch("hospital_management.read_json")
    def test_change_doctor_for_patient(self, mock_read_json, mock_write_json):
        mock_read_json.side_effect = [
            [{"id": "P1", "doctorId": "D1", "isDeleted": False}],  # patients
            [{"id": "D2", "isDeleted": False}]  # doctors
        ]
        self.hm.change_doctor_for_patient("P1", "D2")
        mock_write_json.assert_called()

if __name__ == "__main__":
    unittest.main()