
from hospital_management import HospitalManager

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