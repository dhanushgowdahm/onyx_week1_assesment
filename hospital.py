import json
from datetime import datetime
import json
from abc import ABC, abstractmethod
from collections import defaultdict

def backup_filename(file):
    # E.g., patients.json → patients_backup.json
    if file.endswith('.json'):
        return file.replace('.json', '_backup.json')
    else:
        return file + '_backup'

def log_action(action, filetitle, status):
    log_entry = {
        "timestamp": datetime.now().isoformat(timespec='seconds'),
        "action": action,
        "file": filetitle,
        "status": status
    }
    try:
        # Append to logs.json
        logs = []
        try:
            with open("logs.json", 'r') as lfile:
                logs = json.load(lfile)
        except Exception:
            pass
        logs.append(log_entry)
        with open("logs.json", 'w') as lfile:
            json.dump(logs, lfile, indent=2)
    except Exception as e:
        print(f"Logging error: {e}")

def write_json(file, data):
    try:
        with open(file, 'w') as main_f:
            json.dump(data, main_f, indent=2)
        log_action("write", file, "opened with write mode")

        backup_file = backup_filename(file)
        with open(backup_file, 'w') as backup_f:
            json.dump(data, backup_f, indent=2)
        log_action("write_backup", backup_file, "backup added ")
    except Exception as e:
        log_action("write", file, f"error: {str(e)}")

def read_json(file):
    try:
        with open(file, 'r') as f:
            data = json.load(f)
        log_action("read", file, "read operation")
        return data
    except Exception as e:
        log_action("read", file, f"error: {str(e)}")
        # Try reading backup
        try:
            backup_file = backup_filename(file)
            with open(backup_file, 'r') as bf:
                data = json.load(bf)
            log_action("read_backup", backup_file, "ok")
            return data
        except Exception as be:
            log_action("read_backup", backup_file, f"error: {str(be)}")
            return []


#  Abstract Base Classes
class Entity(ABC):
    def __init__(self, id):
        self._id = str(id) #to prevent direct modification outside the class, modifying it will give <can't assign to property>
        self._is_deleted = False  #using is_deleted field for soft delete

    @property  #makes this method accessible like an attribute (obj.id)
    def id(self):
        return self._id

    @property
    def is_deleted(self):
        return self._is_deleted

    def mark_deleted(self):
        self._is_deleted = True

    @abstractmethod
    def to_dict(self):  #to convert values into dictionary values to add to json
        pass


class Person(Entity):
    def __init__(self, id, name, age, gender):
        super().__init__(id)
        self.name = name
        self.age = int(age)
        self.gender = gender.capitalize()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "isDeleted": self.is_deleted
        }


#  Patient, Doctor, Bed Classes
class Patient(Person):
    def __init__(self, id, name, age, gender, priority="yellow"):
        super().__init__(id, name, age, gender)
        self.priority = priority.capitalize()
        self.present_medication = []
        self.past_medication = []
        self.doctor_id = None  # Initially unassigned
        self.bed_id = None     # Initially unassigned

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


class Bed(Entity):
    def __init__(self, id, bed_type="General", ward="A"):
        super().__init__(id)
        self.bed_type = bed_type  # e.g., General, ICU, Special
        self.ward = ward          # e.g., A, B, C...
        self.patient_id = None
        self.priority = None
        self.status = "Vacant"

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


# ---------- Hospital Manager ----------
class HospitalManager:
    def __init__(self):
        self.patient_file = "patients.json"
        self.doctor_file = "doctors.json"
        self.bed_file = "beds.json"
        self.facilities = {
             "X-Ray": 500,
             "Blood Test": 300,
             "MRI": 5000,
             "CT Scan": 4000,
             "ECG": 800,
             "Physiotherapy": 1000
         }


    def assign_doctor_to_patient(self, patient_id, doctor_id):
        patients = read_json(self.patient_file)
        doctors = read_json(self.doctor_file)

        doctor_exists = any(doc["id"] == doctor_id for doc in doctors)
        if not doctor_exists:
            print(f"Doctor with ID {doctor_id} not found.")
            return

        updated = False
        for patient in patients:
            if patient["id"] == patient_id:
                patient["doctorId"] = doctor_id
                updated = True
                break

        if updated:
            write_json(self.patient_file, patients)
            print(f"Assigned Doctor {doctor_id} to Patient {patient_id}")
        else:
            print(f"Patient with ID {patient_id} not found.")


    def assign_bed_to_patient(self, patient_id, bed_id):
        patients = read_json(self.patient_file)
        beds = read_json(self.bed_file)

        bed = next((b for b in beds if b["id"] == bed_id), None)
        if not bed:
            print(f"Bed with ID {bed_id} not found.")
            return

        patient = next((p for p in patients if p["id"] == patient_id), None)
        if not patient:
            print(f"Patient with ID {patient_id} not found.")
            return

        updated_patient = False
        updated_bed = False

        for p in patients:
            if p["id"] == patient_id:
                p["bedId"] = bed_id
                updated_patient = True
                break

        for b in beds:
            if b["id"] == bed_id:
                b["patientId"] = patient_id
                b["priority"] = patient.get("priority", "low")
                b["status"] = "occupied"  # <-- update bed status here
                updated_bed = True
                break

        if updated_patient and updated_bed:
            write_json(self.patient_file, patients)
            write_json(self.bed_file, beds)
            print(f"Assigned Bed {bed_id} to Patient {patient_id} and marked bed as occupied.")
        else:
            print("Assignment failed.")


    def get_patients_by_doctor(self, doctor_id):
        patients = read_json(self.patient_file)
        doctor_patients = [p for p in patients if p.get("doctorId") == doctor_id and not p.get("isDeleted", False)]

        if not doctor_patients:
            print(f"No patients found for Doctor ID: {doctor_id}")
            return

        # Priority map: higher value = higher priority
        priority_order = {"red": 3, "yellow": 2, "green": 1}
        doctor_patients.sort(key=lambda p: -priority_order.get(p.get("priority", "").lower(), 0))

        print(f"\nPatients assigned to Doctor ID: {doctor_id} (sorted by priority)")
        for p in doctor_patients:
            print(f"ID: {p['id']}, Name: {p['name']}, Age: {p['age']}, Gender: {p['gender']}, Priority: {p['priority']}")

    def generate_id(self, file, prefix):  #generated Id (P0004)
        try:
            data = read_json(file)
            if not data:
                return f"{prefix}0001" #prefix P,D,B
            max_num = max(int(d["id"][1:]) for d in data if d["id"].startswith(prefix))
            return f"{prefix}{max_num + 1:04d}" #keeps padding to 4 digits
        except Exception:
            return f"{prefix}0001"

    def save_entity(self, file, entity):
        data = read_json(file)
        data.append(entity.to_dict()) #fetch json and append to json before writing back
        write_json(file, data)

    def add_patient(self, name, age, gender, priority="yellow"): #priorities(red being highest,green lowest)
        pid = self.generate_id(self.patient_file, "P")
        patient = Patient(pid, name, age, gender, priority)
        self.save_entity(self.patient_file, patient)
        print(f" Patient added: {pid}")

    def add_doctor(self, name, age, gender, specialization):
        did = self.generate_id(self.doctor_file, "D")
        doctor = Doctor(did, name, age, gender, specialization)
        self.save_entity(self.doctor_file, doctor)
        print(f" Doctor added: {did}")

    def add_bed(self, bed_type="General", ward="A"):
        bid = self.generate_id(self.bed_file, "B")
        bed = Bed(bid, bed_type=bed_type.capitalize(), ward=ward.upper())
        self.save_entity(self.bed_file, bed)
        print(f" Bed added: {bid} | Type: {bed_type.capitalize()} | Ward: {ward.upper()}")

    def discharge_patient(self, patient_id):
        patients = read_json(self.patient_file)
        beds = read_json(self.bed_file)

        found = False
        for p in patients:
            if p["id"] == patient_id and not p["isDeleted"]:
                p["isDeleted"] = True
                found = True
                break

        if not found:
            print(" Patient not found or already discharged.")
            return

        for bed in beds:  #empty the occupied bed details
            if bed["patientId"] == patient_id:
                bed["patientId"] = None
                bed["doctorId"] = None
                bed["priority"] = None
                bed["status"] = "Vacant"

        write_json(self.patient_file, patients)
        write_json(self.bed_file, beds)
        print(f" Patient {patient_id} discharged, bed freed.")

    def update_patient_priority(self, patient_id, new_priority):
        patients = read_json(self.patient_file)
        beds = read_json(self.bed_file)

        found = False
        for p in patients:
            if p["id"] == patient_id and not p["isDeleted"]:
                p["priority"] = new_priority.capitalize()
                found = True
                break

        if found:
            for b in beds:
                if b.get("patientId") == patient_id and not b["isDeleted"]:
                    b["priority"] = new_priority.capitalize()
            write_json(self.patient_file, patients)
            write_json(self.bed_file, beds)
            print(f"Updated priority for {patient_id} to {new_priority}")
        else:
            print("Patient not found or deleted.")


    def show_bed_status(self):
       beds = read_json(self.bed_file)
       if not beds:
           print("No beds available.")
           return

       ward_summary = defaultdict(lambda: {
           "General_total": 0, "General_occupied": 0,
           "ICU_total": 0, "ICU_occupied": 0,
           "Special_total": 0, "Special_occupied": 0
       })

       for bed in beds:
           if bed.get("isDeleted", False):
               continue
           ward = bed.get("ward", "Unknown")
           bed_type = bed.get("bed_type", "").lower()
           status = bed.get("status", "").lower()

           key_total = f"{bed_type.capitalize()}_total"
           key_occupied = f"{bed_type.capitalize()}_occupied"
           if key_total in ward_summary[ward]:
               ward_summary[ward][key_total] += 1
               if status == "occupied":
                   ward_summary[ward][key_occupied] += 1

       print("---- Bed Summary by Ward ----")
       for ward, counts in ward_summary.items():
           print(f"Ward: {ward}")
           print(f"  General: {counts['General_occupied']} occupied / {counts['General_total']} total")
           print(f"  ICU    : {counts['ICU_occupied']} occupied / {counts['ICU_total']} total")
           print(f"  Special: {counts['Special_occupied']} occupied / {counts['Special_total']} total")
       print("-" * 60)

       # Now print the full bed status table
       print(f"{'Bed ID':<8} {'Ward':<6} {'Type':<10} {'Status':<10} {'Patient ID':<12} {'Priority':<10}")
       print("-" * 60)
       for bed in beds:
           if not bed.get("isDeleted", False):
               print(f"{bed['id']:<8} {bed['ward']:<6} {bed['bed_type']:<10} {bed['status']:<10} "
                     f"{str(bed.get('patientId') or '-'): <12} {str(bed.get('priority') or '-'): <10}")

    def show_patients(self):
        patients = read_json(self.patient_file)
        print("\n Patients List:")
        for p in patients:
            if not p["isDeleted"]:
                print(f"ID: {p['id']}, Name: {p['name']}, Age: {p['age']}, Gender: {p['gender']}, Priority: {p['priority']}")

    def show_doctors(self):
        doctors = read_json(self.doctor_file)
        print("\n Doctors List:")
        for d in doctors:
            if not d["isDeleted"]:
                print(f"ID: {d['id']}, Name: {d['name']}, Age: {d['age']}, Gender: {d['gender']}, Specialization: {d['specialization']}")

    def doctor_visit(self, patient_id):
        patients = read_json(self.patient_file)
        for p in patients:
            if p["id"] == patient_id and not p["isDeleted"]:
                print(f"\n Doctor Visit for {p['name']} (ID: {p['id']}, Age: {p['age']}, Gender: {p['gender']})")
                print(f"Current Medications: {', '.join(p['present_medication']) or 'None'}")
                print(f"Past Medications: {', '.join(p['past_medication']) or 'None'}")

                to_remove = input("Enter medications to stop (comma-separated): ").strip()
                if to_remove:
                    to_remove_list = [m.strip() for m in to_remove.split(",")]
                    for m in to_remove_list:
                        if m in p["present_medication"]:
                            p["present_medication"].remove(m)
                        p["past_medication"].append(m)

                to_add = input("Enter new medications (comma-separated): ").strip()
                if to_add:
                    for med in map(str.strip, to_add.split(",")):
                        if med:
                            p["present_medication"].append(med)

                write_json(self.patient_file, patients)
                print(" Medications updated.")
                return

        print(" Patient not found or deleted.")

    def fetch_patients_by_doctor(self, doctor_id):
        beds = read_json(self.bed_file)
        patients = read_json(self.patient_file)

        priority_map = {"red": 3, "yellow": 2, "green": 1, None: 0}

        # Filter and sort beds assigned to the given doctor, by patient priority
        filtered_beds = [
            bed for bed in beds
            if not bed["isDeleted"]
            and bed["doctorId"] == doctor_id
            and bed["status"] == "Occupied"
        ]

        sorted_beds = sorted( filtered_beds, key=lambda b: -priority_map.get((b.get("priority") or "").lower(), 0)) #-priority because to get red-3 first before yellow-2


        if not sorted_beds:
            print(f" No patients found for Doctor ID: {doctor_id}")
            return

        print(f"\n Patients under Doctor {doctor_id} (sorted by priority):")
        for bed in sorted_beds:
            patient = next((p for p in patients if p["id"] == bed["patientId"] and not p["isDeleted"]), None)
            if patient:
                print(f"🔹 Patient ID: {patient['id']}, Name: {patient['name']}, Age: {patient['age']}, "
                      f"Gender: {patient['gender']}, Priority: {patient['priority']}, Bed ID: {bed['id']}")

    def change_doctor_for_bed(self, bed_id, new_doctor_id):
        beds = read_json(self.bed_file)
        doctors = read_json(self.doctor_file)

        bed = next((b for b in beds if b["id"] == bed_id and not b["isDeleted"]), None)
        doctor = next((d for d in doctors if d["id"] == new_doctor_id and not d["isDeleted"]), None)

        if not bed:
            print(" Bed not found or deleted.")
            return
        if not doctor:
            print(" Doctor not found or deleted.")
            return
        if bed["status"] != "Occupied":
            print(" Bed is not currently occupied.")
            return

        old_doctor_id = bed.get("doctorId")
        bed["doctorId"] = new_doctor_id
        write_json(self.bed_file, beds)

        print(f" Doctor for Bed {bed_id} changed from {old_doctor_id} to {new_doctor_id}.")

    def billing_menu(self, patient_id):
        patients = read_json(self.patient_file)
        patient = next((p for p in patients if p["id"] == patient_id and not p["isDeleted"]), None)

        if not patient:
            print(" Patient not found or already deleted.")
            return

        if "billing" not in patient:
            patient["billing"] = []

        print(f"\n Current Bill for {patient['name']} (ID: {patient_id}):")
        total = sum(self.facilities.get(f, 0) for f in patient["billing"])
        print(f"Total Amount: ₹{total}")
        print("Added Facilities:", ", ".join(patient['billing']) or "None")

        print("\nAvailable Facilities:")
        for i, (f, price) in enumerate(self.facilities.items(), 1):
            print(f"{i}. {f} - ₹{price}")

        try:
            choice = input("Enter facility number to add (or leave blank to cancel): ").strip()
            if not choice:
                return
            choice = int(choice)
            facility = list(self.facilities.keys())[choice - 1]
            patient["billing"].append(facility)
            write_json(self.patient_file, patients)
            print(f" {facility} added to bill.")
        except (IndexError, ValueError):
            print(" Invalid selection.")

    def change_bed_for_patient(self, patient_id, new_bed_id):
       patients = read_json(self.patient_file)
       beds = read_json(self.bed_file)

       patient = next((p for p in patients if p["id"] == patient_id and not p.get("isDeleted", False)), None)
       if not patient:
           print(f"Patient with ID {patient_id} not found.")
           return

       new_bed = next((b for b in beds if b["id"] == new_bed_id and not b.get("isDeleted", False)), None)
       if not new_bed:
           print(f"New Bed with ID {new_bed_id} not found.")
           return

       if new_bed.get("status") == "occupied":
           print(f"Bed {new_bed_id} is already occupied.")
           return

       old_bed_id = patient.get("bedId")

       # Free up the old bed
       for b in beds:
           if b["id"] == old_bed_id:
               b["patientId"] = None
               b["priority"] = None
               b["status"] = "vacant"
               break

       # Assign new bed
       for b in beds:
           if b["id"] == new_bed_id:
               b["patientId"] = patient_id
               b["priority"] = patient.get("priority", "low")
               b["status"] = "occupied"
               break

       # Update patient
       for p in patients:
           if p["id"] == patient_id:
               p["bedId"] = new_bed_id
               break

       write_json(self.patient_file, patients)
       write_json(self.bed_file, beds)
       print(f"Changed bed for Patient {patient_id} from Bed {old_bed_id} to Bed {new_bed_id}.")

    def change_doctor_for_patient(self, patient_id, new_doctor_id):
        patients = read_json(self.patient_file)
        doctors = read_json(self.doctor_file)

        # Find the patient
        patient = next((p for p in patients if p["id"] == patient_id and not p.get("isDeleted", False)), None)
        if not patient:
            print(f"Patient with ID {patient_id} not found.")
            return

        # Find the new doctor
        doctor = next((d for d in doctors if d["id"] == new_doctor_id and not d.get("isDeleted", False)), None)
        if not doctor:
            print(f"Doctor with ID {new_doctor_id} not found.")
            return

        # Update doctorId
        old_doctor_id = patient.get("doctorId")
        for p in patients:
            if p["id"] == patient_id:
                p["doctorId"] = new_doctor_id
                break

        write_json(self.patient_file, patients)
        print(f"Changed doctor for Patient {patient_id} from Doctor {old_doctor_id} to Doctor {new_doctor_id}.")


# ---------- Main Menu ----------
def main():
    h = HospitalManager()
    while True:
        print("\n Hospital Management System")
        print("1. Add Patient")
        print("2. Add Doctor")
        print("3. Add Bed")
        print("4. Assign Bed to Patient")
        print("5. assign doctor to patient")
        print("6. Show Bed Status")
        print("7. Show Patients")
        print("8. Show Doctors")
        print("9. Update Patient Priority")
        print("10. Doctor Visit (Update Medication)")
        print("11. Fetch Patients by Doctor (Sorted by Priority)")
        print("12. change Bed for patient: ")
        print("13. Billing")
        print("14. Discharge Patient")
        print("15> change doctor for patient")


        print("0. Exit")

        choice = input("Enter choice: ")
        try:
            if choice == "1":
                name = input("Enter name: ")
                age = int(input("Enter age: "))
                gender = input("Enter gender (Male/Female/Other): ")
                priority = input("Enter priority (red/yellow/green): ") or "yellow"
                h.add_patient(name, age, gender, priority)
            elif choice == "2":
                name = input("Enter name: ")
                age = int(input("Enter age: "))
                gender = input("Enter gender (Male/Female/Other): ")
                specialization = input("Enter specialization: ")
                h.add_doctor(name, age, gender, specialization)
            elif choice == "3":
                bed_type_input = input("Enter bed type (General/ICU/Special): ") or "General"
                ward_input = input("Enter ward (A/B/C etc.): ") or "A"
                h.add_bed(bed_type_input, ward_input)
            elif choice == "4":
                pid = input("Enter patient ID: ")
                bid = input("Enter Bed Id: ")
                h.assign_bed_to_patient(pid, bid)
            elif choice == "5":
                pid = input("Enter patient ID: ")
                did = input("Enter Doctor Id: ")
                h.assign_doctor_to_patient(pid, did)
            elif choice == "6":
                h.show_bed_status()
            elif choice == "7":
                h.show_patients()
            elif choice == "8":
                h.show_doctors()
            elif choice == "9":
                pid = input("Enter patient ID: ")
                pr = input("Enter new priority (red/yellow/green): ")
                h.update_patient_priority(pid, pr)
            elif choice == "10":
                pid = input("Enter patient ID: ")
                h.doctor_visit(pid)
            elif choice == "11":
                did = input("Enter doctor ID: ")
                h.get_patients_by_doctor(did)
            elif choice == "12":
                pid = input("Enter Patient ID: ")
                new_did = input("Enter Bed ID: ")
                h.change_bed_for_patient(pid, new_did)
            elif choice == "13":
                pid = input("Enter patient ID: ")
                h.billing_menu(pid)
            elif choice == "14":
                pid = input("Enter patient ID: ")
                h.discharge_patient(pid)
            elif choice == "15":
                pid = input("Enter patient ID: ")
                did = input("Enter Doctor Id: ")
                h.change_doctor_for_patient(pid, did)

            elif choice == "0":
                print("👋 Exiting...")
                # upload_to_mongodb()
                break
            else:
                print(" Invalid choice.")
        except ValueError:
            print(" Invalid input. Please enter a valid number or option.")

if __name__ == "__main__":
    main()