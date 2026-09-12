import json
import os
import sys
from datetime import date, datetime
from pathlib import Path
from PIL import Image

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import DATA_DIR, PHOTOS_DIR
from app.core.database import init_db, get_db_session
from app.models.student import Student, StudentFeeInstallment
from app.modules.students.controllers import StudentController

RAW_STUDENTS_DATA = [
    {
        "source_image": "IMG_3057.png",
        "has_photo": True,
        "crop_box_ratios": [0.778, 0.228, 0.955, 0.395],
        "name": "Mohammed Irfan Khatri",
        "father_name": "Yunus",
        "mother_name": "Rukshna",
        "dob": "2004-07-05",
        "father_occupation": None,
        "college_school": None,
        "course_name": "Master Architecture",
        "year_sem": None,
        "mobile_no": "7878849949",
        "email": "irfankhatri07878@gmail.com",
        "father_contact_no": "9828648930",
        "alternate_contact_no": None,
        "permanent_address": "Islampura Mohalla, Ward No-5, Laxmangarh",
        "district": "Sikar",
        "state": "Rajasthan",
        "pin_code": "332311",
        "aadhar_no": "925588487474",
        "status": "Active",
        "admission_date": "2024-08-19",
        "is_online": True,
        "online_reg_no": "Online Khatri",
        "total_fee": 84000.0,
        "discount_amount": 0.0,
        "net_fee": 84000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 20000.0, "paid_amount": 20000.0, "due_date": "2024-08-19", "payment_date": "2024-08-19", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 15000.0, "paid_amount": 15000.0, "due_date": "2025-04-23", "payment_date": "2025-04-23", "payment_mode": "Cash"},
            {"installment_no": 3, "installment_label": "3rd", "due_amount": 5000.0, "paid_amount": 5000.0, "due_date": "2025-10-31", "payment_date": "2025-10-31", "payment_mode": "Cash"},
            {"installment_no": 4, "installment_label": "4th", "due_amount": 5000.0, "paid_amount": 0.0, "due_date": "2026-04-28", "payment_mode": "Cash"},
            {"installment_no": 5, "installment_label": "5th", "due_amount": 9000.0, "paid_amount": 0.0, "due_date": "2026-01-31", "payment_mode": "Cash"},
            {"installment_no": 6, "installment_label": "6th", "due_amount": 10000.0, "paid_amount": 0.0, "due_date": "2026-03-09", "payment_mode": "Cash"},
            {"installment_no": 7, "installment_label": "7th", "due_amount": 20000.0, "paid_amount": 0.0, "due_date": "2026-03-23", "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3058.png",
        "has_photo": True,
        "crop_box_ratios": [0.772, 0.228, 0.952, 0.395],
        "name": "Pardeep Kumar",
        "father_name": "Om Parkash Goswami",
        "mother_name": "Manju Devi",
        "dob": "2004-03-09",
        "father_occupation": "Foreign",
        "college_school": "College",
        "course_name": "Architecture",
        "year_sem": None,
        "mobile_no": "7690890527",
        "email": None,
        "father_contact_no": "9680840527",
        "alternate_contact_no": "7690890527",
        "permanent_address": "Raghunathgarh",
        "district": "Sikar",
        "state": "Rajasthan",
        "pin_code": None,
        "aadhar_no": "878100935553",
        "status": "Active",
        "admission_date": "2024-07-28",
        "is_online": True,
        "online_reg_no": "Same Pradeep",
        "total_fee": 25000.0,
        "discount_amount": 0.0,
        "net_fee": 25000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 11000.0, "paid_amount": 11000.0, "due_date": "2024-07-28", "payment_date": "2024-07-28", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 14000.0, "paid_amount": 0.0, "due_date": "2026-03-30", "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3059.png",
        "has_photo": False,
        "name": "Faizan Gour",
        "father_name": "Mo. Shafi Gour",
        "mother_name": "Afsana Bano",
        "dob": "2005-03-17",
        "father_occupation": "Saudi",
        "college_school": "Islamia Sen. Sec. School",
        "course_name": "Architecture",
        "year_sem": None,
        "mobile_no": "8107753637",
        "email": "mohammedsofi1238@gmail.com",
        "father_contact_no": "8503062066",
        "alternate_contact_no": "7073009293 (Sister)",
        "permanent_address": "Shaikhpura Mohalla",
        "district": "Sikar",
        "state": "Rajasthan",
        "pin_code": "332001",
        "aadhar_no": "369062792255",
        "status": "Active",
        "admission_date": "2024-06-22",
        "is_online": True,
        "online_reg_no": "16/10/25",
        "total_fee": 60000.0,
        "discount_amount": 0.0,
        "net_fee": 60000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 9000.0, "paid_amount": 9000.0, "due_date": "2024-06-22", "payment_date": "2024-06-22", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-07-12", "payment_date": "2024-07-12", "payment_mode": "Cash"},
            {"installment_no": 3, "installment_label": "3rd", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-11-30", "payment_date": "2024-11-30", "payment_mode": "Cash"},
            {"installment_no": 4, "installment_label": "4th", "due_amount": 31000.0, "paid_amount": 31000.0, "due_date": "2024-12-24", "payment_date": "2024-12-24", "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3060.png",
        "has_photo": True,
        "crop_box_ratios": [0.765, 0.252, 0.942, 0.425],
        "name": "Arman Khan",
        "father_name": "Ayub Khan",
        "mother_name": "Firdosh Bano",
        "dob": "2005-04-23",
        "father_occupation": "Saudi Vakala",
        "college_school": "Govt. Sr. Sec. School Sabalpura",
        "course_name": "Architectural",
        "year_sem": None,
        "mobile_no": "9079067895",
        "email": "armankhan90796@gmail.com",
        "father_contact_no": "7737805296",
        "alternate_contact_no": None,
        "permanent_address": "Sabalpura, Sikar",
        "district": "Sikar",
        "state": "Rajasthan",
        "pin_code": "332001",
        "aadhar_no": "735851697377",
        "status": "Active",
        "admission_date": "2023-10-05",
        "is_online": True,
        "online_reg_no": "C02402292929528",
        "total_fee": 60000.0,
        "discount_amount": 0.0,
        "net_fee": 60000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 5000.0, "paid_amount": 5000.0, "due_date": "2023-10-05", "payment_date": "2023-10-05", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 15000.0, "paid_amount": 15000.0, "due_date": "2023-11-08", "payment_date": "2023-11-08", "payment_mode": "Cash"},
            {"installment_no": 3, "installment_label": "3rd", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-02-09", "payment_date": "2024-02-09", "payment_mode": "Cash"},
            {"installment_no": 4, "installment_label": "4th", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-04-29", "payment_date": "2024-04-29", "payment_mode": "Cash"},
            {"installment_no": 5, "installment_label": "5th", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-07-18", "payment_date": "2024-07-18", "payment_mode": "Cash"},
            {"installment_no": 6, "installment_label": "6th", "due_amount": 10000.0, "paid_amount": 0.0, "due_date": "2026-02-07", "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3061.png",
        "has_photo": False,
        "name": "Yogita Jangir",
        "father_name": "Omprakash Jangir",
        "mother_name": "Saroj Jangir",
        "dob": None,
        "father_occupation": None,
        "college_school": None,
        "course_name": "Full Stack Development / CAD",
        "year_sem": None,
        "mobile_no": "8441884272",
        "email": None,
        "father_contact_no": "7891763671",
        "alternate_contact_no": None,
        "permanent_address": "Abhaipura (Palsana)",
        "district": "Sikar",
        "state": "Rajasthan",
        "pin_code": None,
        "aadhar_no": None,
        "status": "Active",
        "admission_date": "2024-07-08",
        "is_online": False,
        "total_fee": 65000.0,
        "discount_amount": 0.0,
        "net_fee": 65000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-07-08", "payment_date": "2024-07-08", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 20000.0, "paid_amount": 20000.0, "due_date": "2024-11-04", "payment_date": "2024-11-04", "payment_mode": "Cash"},
            {"installment_no": 3, "installment_label": "3rd", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-12-30", "payment_date": "2024-12-30", "payment_mode": "Cash"},
            {"installment_no": 4, "installment_label": "4th", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2025-05-26", "payment_date": "2025-05-26", "payment_mode": "Cash"},
            {"installment_no": 5, "installment_label": "5th", "due_amount": 5000.0, "paid_amount": 5000.0, "due_date": "2025-10-01", "payment_date": "2025-10-01", "payment_mode": "Cash"},
            {"installment_no": 6, "installment_label": "6th", "due_amount": 10000.0, "paid_amount": 0.0, "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3062.png",
        "has_photo": True,
        "crop_box_ratios": [0.805, 0.210, 0.988, 0.390],
        "name": "Arman Khan",
        "father_name": "Habib Khan",
        "mother_name": "Kismat Bano",
        "dob": "2007-07-16",
        "father_occupation": None,
        "college_school": "Rajiv Gandhi",
        "course_name": "Land Survey",
        "year_sem": None,
        "mobile_no": "7737290296",
        "email": None,
        "father_contact_no": "9166661210",
        "alternate_contact_no": "8441843515 (Mother)",
        "permanent_address": "Beri Khurd",
        "district": "Nagaur",
        "state": "Rajasthan",
        "pin_code": None,
        "aadhar_no": "826553520424",
        "status": "Active",
        "admission_date": "2024-02-20",
        "is_online": True,
        "online_reg_no": "Land Survey",
        "total_fee": 30000.0,
        "discount_amount": 0.0,
        "net_fee": 30000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-02-20", "payment_date": "2024-02-20", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-05-10", "payment_date": "2024-05-10", "payment_mode": "Cash"},
            {"installment_no": 3, "installment_label": "3rd", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-07-01", "payment_date": "2024-07-01", "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3063.png",
        "has_photo": True,
        "crop_box_ratios": [0.788, 0.220, 0.975, 0.392],
        "name": "Akhilesh Jangir",
        "father_name": "Suresh Kumar Jangir",
        "mother_name": "Sanju Devi",
        "dob": "1999-10-04",
        "father_occupation": None,
        "college_school": "Seth G.B. Podar College",
        "course_name": "Full Stack Development / CAD",
        "year_sem": None,
        "mobile_no": "8619021071",
        "email": "akhileshjangir650@gmail.com",
        "father_contact_no": "9691729241",
        "alternate_contact_no": None,
        "permanent_address": "Bheriwara Khurd, Mukundgarh",
        "district": "Jhunjhunu",
        "state": "Rajasthan",
        "pin_code": "333705",
        "aadhar_no": "549117844655",
        "status": "Active",
        "admission_date": "2025-05-28",
        "is_online": True,
        "online_reg_no": "Online Verified",
        "total_fee": 40000.0,
        "discount_amount": 0.0,
        "net_fee": 40000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2025-05-28", "payment_date": "2025-05-28", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 5000.0, "paid_amount": 5000.0, "due_date": "2025-10-07", "payment_date": "2025-10-07", "payment_mode": "Cash"},
            {"installment_no": 3, "installment_label": "3rd", "due_amount": 5000.0, "paid_amount": 5000.0, "due_date": "2025-11-27", "payment_date": "2025-11-27", "payment_mode": "Cash"},
            {"installment_no": 4, "installment_label": "4th", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2025-12-12", "payment_date": "2025-12-12", "payment_mode": "Cash"},
            {"installment_no": 5, "installment_label": "5th", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2026-01-30", "payment_date": "2026-01-30", "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3064.png",
        "has_photo": False,
        "name": "Nadeem Khan",
        "father_name": "Jabir Khan",
        "mother_name": "Khatun Bano",
        "dob": "2006-06-10",
        "father_occupation": "Car Driver",
        "college_school": "Choudhary AR College",
        "course_name": "Master / R.K.T.K.L",
        "year_sem": None,
        "mobile_no": "9664126115",
        "email": "nadimkhan907900@gmail.com",
        "father_contact_no": "9660909386 (Bro)",
        "alternate_contact_no": None,
        "permanent_address": "Kayamkhani Hostel, Vill-Kanwarwas",
        "district": "Churu",
        "state": "Rajasthan",
        "pin_code": "331403",
        "aadhar_no": None,
        "status": "Active",
        "admission_date": "2024-05-08",
        "is_online": True,
        "online_reg_no": "Master",
        "total_fee": 65500.0,
        "discount_amount": 0.0,
        "net_fee": 65500.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-05-08", "payment_date": "2024-05-08", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 25500.0, "paid_amount": 25500.0, "due_date": "2024-06-14", "payment_date": "2024-06-14", "payment_mode": "Cash"},
            {"installment_no": 3, "installment_label": "3rd", "due_amount": 15000.0, "paid_amount": 15000.0, "due_date": "2024-10-28", "payment_date": "2024-10-28", "payment_mode": "Cash"},
            {"installment_no": 4, "installment_label": "4th", "due_amount": 15000.0, "paid_amount": 0.0, "due_date": "2025-05-12", "payment_mode": "PhonePe"},
        ]
    },
    {
        "source_image": "IMG_3065.png",
        "has_photo": True,
        "crop_box_ratios": [0.792, 0.222, 0.980, 0.402],
        "name": "Manisha Kumawat",
        "father_name": "Kailash Chand",
        "mother_name": "Sita Devi",
        "dob": "2007-03-11",
        "father_occupation": None,
        "college_school": "BND Nechhwa Sikar",
        "course_name": "CAD / IT",
        "year_sem": None,
        "mobile_no": "6375832862",
        "email": None,
        "father_contact_no": "9043669455 (Sadur)",
        "alternate_contact_no": None,
        "permanent_address": "BND College Ke Piche, Nechhwa, Sikar",
        "district": "Sikar",
        "state": "Rajasthan",
        "pin_code": None,
        "aadhar_no": "829661380975",
        "status": "Active",
        "admission_date": "2026-01-10",
        "is_online": False,
        "total_fee": 52000.0,
        "discount_amount": 0.0,
        "net_fee": 52000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 30000.0, "paid_amount": 30000.0, "due_date": "2026-01-10", "payment_date": "2026-01-10", "payment_mode": "GPay"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 22000.0, "paid_amount": 0.0, "due_date": "2026-09-03", "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3066.png",
        "has_photo": False,
        "name": "Pradeep Kumar",
        "father_name": "Mula Ram",
        "mother_name": "Omi Devi",
        "dob": "2006-03-15",
        "father_occupation": "Contractor/Business",
        "college_school": "Prince Academy",
        "course_name": "PG Expert Master (Builder Gold)",
        "year_sem": None,
        "mobile_no": "9799262326",
        "email": "prajapatpradeep597@gmail.com",
        "father_contact_no": "9928304572",
        "alternate_contact_no": "9521453100 (Bro)",
        "permanent_address": "Lunda, Post-Roidhonu, Nagaur",
        "district": "Nagaur",
        "state": "Rajasthan",
        "pin_code": "341001",
        "aadhar_no": "754121428104",
        "status": "Dropped",
        "admission_date": "2025-07-24",
        "is_online": True,
        "online_reg_no": "Same Pradeep",
        "total_fee": 5000.0,
        "discount_amount": 0.0,
        "net_fee": 5000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 5000.0, "paid_amount": 5000.0, "due_date": "2025-07-24", "payment_date": "2025-07-24", "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3067.png",
        "has_photo": True,
        "crop_box_ratios": [0.772, 0.252, 0.952, 0.418],
        "name": "Sushil Kumar",
        "father_name": "Bajrang Lal",
        "mother_name": "Indira Devi",
        "dob": "2003-10-10",
        "father_occupation": "Carpenter",
        "college_school": "Pandit Deendayal Upadhyaya Shekhawati University",
        "course_name": "Architecture",
        "year_sem": None,
        "mobile_no": "7877091323",
        "email": "skj724774@gmail.com",
        "father_contact_no": "9783353334",
        "alternate_contact_no": None,
        "permanent_address": "Tatanwa (Sikar)",
        "district": "Sikar",
        "state": "Rajasthan",
        "pin_code": "332042",
        "aadhar_no": "808635749632",
        "status": "Active",
        "admission_date": "2024-09-21",
        "is_online": True,
        "online_reg_no": "C02507252705835",
        "total_fee": 74000.0,
        "discount_amount": 0.0,
        "net_fee": 74000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 15000.0, "paid_amount": 15000.0, "due_date": "2024-09-21", "payment_date": "2024-09-21", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 5000.0, "paid_amount": 5000.0, "due_date": "2024-11-25", "payment_date": "2024-11-25", "payment_mode": "Cash"},
            {"installment_no": 3, "installment_label": "3rd", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2025-02-01", "payment_date": "2025-02-01", "payment_mode": "Cash"},
            {"installment_no": 4, "installment_label": "4th", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2025-03-17", "payment_date": "2025-03-17", "payment_mode": "Cash"},
            {"installment_no": 5, "installment_label": "5th", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2025-07-25", "payment_date": "2025-07-25", "payment_mode": "Cash"},
            {"installment_no": 6, "installment_label": "6th", "due_amount": 20000.0, "paid_amount": 0.0, "payment_mode": "PhonePe"},
            {"installment_no": 7, "installment_label": "7th", "due_amount": 4000.0, "paid_amount": 0.0, "remarks": "Incentive Anees", "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3068.png",
        "has_photo": True,
        "crop_box_ratios": [0.765, 0.188, 0.940, 0.352],
        "name": "Sunil Bangarwa",
        "father_name": "Ramdeva Ram",
        "mother_name": "Godavari Devi",
        "dob": "2002-10-01",
        "father_occupation": None,
        "college_school": "P.D.U.S.U",
        "course_name": "Product Design",
        "year_sem": None,
        "mobile_no": "7240763518",
        "email": "sunilbangarva626@gmail.com",
        "father_contact_no": "9982219753",
        "alternate_contact_no": None,
        "permanent_address": "Kachhwa, Sikar, Raj.",
        "district": "Sikar",
        "state": "Rajasthan",
        "pin_code": "332026",
        "aadhar_no": "772107860125",
        "status": "Active",
        "admission_date": "2026-01-31",
        "is_online": True,
        "online_reg_no": "LNC Skep",
        "total_fee": 15000.0,
        "discount_amount": 0.0,
        "net_fee": 15000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2026-01-31", "payment_date": "2026-01-31", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 5000.0, "paid_amount": 0.0, "due_date": "2026-03-10", "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3069.png",
        "has_photo": True,
        "crop_box_ratios": [0.790, 0.238, 0.980, 0.415],
        "name": "Suffiyan Qureshi",
        "father_name": "Sarfaraz Qureshi",
        "mother_name": "Najma Bano",
        "dob": "2001-11-20",
        "father_occupation": "Self-employment",
        "college_school": "CCA",
        "course_name": "Master-Archi",
        "year_sem": None,
        "mobile_no": "8233823001",
        "email": "suffiyanqureshi03@gmail.com",
        "father_contact_no": "9782454504",
        "alternate_contact_no": "8058646519",
        "permanent_address": "3 No Road Aakash Nagar, Guldha Mod, Jhunjhunu",
        "district": "Jhunjhunu",
        "state": "Rajasthan",
        "pin_code": "333001",
        "aadhar_no": "486894635156",
        "status": "Active",
        "admission_date": "2023-11-06",
        "is_online": False,
        "total_fee": 40000.0,
        "discount_amount": 0.0,
        "net_fee": 40000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2023-11-06", "payment_date": "2023-11-06", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-02-15", "payment_date": "2024-02-15", "payment_mode": "Cash"},
            {"installment_no": 3, "installment_label": "3rd", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-05-20", "payment_date": "2024-05-20", "payment_mode": "Cash"},
            {"installment_no": 4, "installment_label": "4th", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-08-17", "payment_date": "2024-08-17", "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3070.png",
        "has_photo": True,
        "crop_box_ratios": [0.765, 0.155, 0.955, 0.355],
        "name": "Abhishek Jangir",
        "father_name": "Pappu Lal Jangir",
        "mother_name": "Kanta Devi",
        "dob": "2002-06-15",
        "father_occupation": None,
        "college_school": None,
        "course_name": "Master Architecture Design",
        "year_sem": None,
        "mobile_no": "6378096240",
        "email": "jangirabhishek947@gmail.com",
        "father_contact_no": None,
        "alternate_contact_no": None,
        "permanent_address": "Ward No. 1 Tatanwa",
        "district": "Sikar",
        "state": "Rajasthan",
        "pin_code": "332042",
        "aadhar_no": "654094574562",
        "status": "Active",
        "admission_date": "2023-08-01",
        "is_online": True,
        "online_reg_no": "31/07/24",
        "total_fee": 125000.0,
        "discount_amount": 0.0,
        "net_fee": 125000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 25000.0, "paid_amount": 25000.0, "due_date": "2023-08-01", "payment_date": "2023-08-01", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 32500.0, "paid_amount": 32500.0, "due_date": "2023-08-02", "payment_date": "2023-08-02", "payment_mode": "Cash"},
            {"installment_no": 3, "installment_label": "3rd", "due_amount": 20000.0, "paid_amount": 20000.0, "due_date": "2024-07-05", "payment_date": "2024-07-05", "payment_mode": "Cash"},
            {"installment_no": 4, "installment_label": "4th", "due_amount": 47500.0, "paid_amount": 0.0, "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3071.png",
        "has_photo": True,
        "crop_box_ratios": [0.772, 0.218, 0.965, 0.402],
        "name": "Sahil Khan",
        "father_name": "Taj Mohammad",
        "mother_name": "Islam Bano",
        "dob": "2003-01-24",
        "father_occupation": None,
        "college_school": None,
        "course_name": "Master in Architecture",
        "year_sem": None,
        "mobile_no": "9649627685",
        "email": "tajk15808@gmail.com",
        "father_contact_no": "9828276872",
        "alternate_contact_no": None,
        "permanent_address": "Kheerwa, Sikar",
        "district": "Sikar",
        "state": "Rajasthan",
        "pin_code": "332316",
        "aadhar_no": "971554352867",
        "status": "Active",
        "admission_date": "2023-07-13",
        "is_online": True,
        "online_reg_no": "Master 29/8/24",
        "total_fee": 43000.0,
        "discount_amount": 0.0,
        "net_fee": 43000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2023-07-13", "payment_date": "2023-07-13", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 5000.0, "paid_amount": 5000.0, "due_date": "2023-11-15", "payment_date": "2023-11-15", "payment_mode": "Cash"},
            {"installment_no": 3, "installment_label": "3rd", "due_amount": 15000.0, "paid_amount": 15000.0, "due_date": "2024-07-24", "payment_date": "2024-07-24", "payment_mode": "Cash"},
            {"installment_no": 4, "installment_label": "4th", "due_amount": 3000.0, "paid_amount": 3000.0, "due_date": "2024-08-10", "payment_date": "2024-08-10", "payment_mode": "Cash"},
            {"installment_no": 5, "installment_label": "5th", "due_amount": 10000.0, "paid_amount": 0.0, "due_date": "2025-10-02", "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3072.png",
        "has_photo": True,
        "crop_box_ratios": [0.778, 0.225, 0.965, 0.402],
        "name": "Mohd. Ali Qureshi",
        "father_name": "Shakir Qureshi",
        "mother_name": "Zainab Qureshi",
        "dob": "2004-08-04",
        "father_occupation": "Shopkeeper",
        "college_school": "Shekhawati College",
        "course_name": "BBA",
        "year_sem": "1st Sem",
        "mobile_no": "6375429295",
        "email": "aliqureshi1420@gmail.com",
        "father_contact_no": "8764618352 (Mother)",
        "alternate_contact_no": None,
        "permanent_address": "Mohalla Qureshiyan Ward No. 40",
        "district": "Sikar",
        "state": "Rajasthan",
        "pin_code": "332001",
        "aadhar_no": "714241241648",
        "status": "Active",
        "admission_date": "2023-10-19",
        "is_online": True,
        "online_reg_no": "29/30 Aug 24",
        "total_fee": 35000.0,
        "discount_amount": 0.0,
        "net_fee": 35000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 25000.0, "paid_amount": 25000.0, "due_date": "2023-10-19", "payment_date": "2023-10-19", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-07-24", "payment_date": "2024-07-24", "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3073.png",
        "has_photo": True,
        "crop_box_ratios": [0.795, 0.220, 0.975, 0.390],
        "name": "Mohit Tamoli",
        "father_name": "Ganesh Tamoli",
        "mother_name": "Santosh Devi",
        "dob": "1995-06-18",
        "father_occupation": "Private Job",
        "college_school": "12th",
        "course_name": "AutoCAD 2D",
        "year_sem": None,
        "mobile_no": "8094488805",
        "email": "tamolimohit58@gmail.com",
        "father_contact_no": "8890516500",
        "alternate_contact_no": "9928618805 (Sister)",
        "permanent_address": "Near By Nediya Ka Jaw, Ward No. 29, Laxmangarh",
        "district": "Sikar",
        "state": "Rajasthan",
        "pin_code": "332311",
        "aadhar_no": "448818637045",
        "status": "Dropped",
        "admission_date": "2024-05-04",
        "is_online": False,
        "total_fee": 34000.0,
        "discount_amount": 0.0,
        "net_fee": 34000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 3000.0, "paid_amount": 3000.0, "due_date": "2024-05-04", "payment_date": "2024-05-04", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 6000.0, "paid_amount": 6000.0, "due_date": "2024-06-25", "payment_date": "2024-06-25", "payment_mode": "Cash"},
            {"installment_no": 3, "installment_label": "3rd", "due_amount": 5000.0, "paid_amount": 5000.0, "due_date": "2024-08-05", "payment_date": "2024-08-05", "payment_mode": "Cash"},
            {"installment_no": 4, "installment_label": "4th", "due_amount": 15000.0, "paid_amount": 15000.0, "due_date": "2024-11-30", "payment_date": "2024-11-30", "payment_mode": "Cash"},
            {"installment_no": 5, "installment_label": "5th", "due_amount": 5000.0, "paid_amount": 0.0, "due_date": "2025-03-17", "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3074.png",
        "has_photo": True,
        "crop_box_ratios": [0.795, 0.210, 0.985, 0.385],
        "name": "Altaf Khan",
        "father_name": "Mohammad Faruk",
        "mother_name": "Sahidan Bano",
        "dob": "2002-06-10",
        "father_occupation": "Earning in abroad",
        "college_school": "Keshwanand Polytechnic College",
        "course_name": "Auto CADD",
        "year_sem": None,
        "mobile_no": "9983259048",
        "email": None,
        "father_contact_no": "9983259048",
        "alternate_contact_no": None,
        "permanent_address": "Vill-Lawanda, Post-Thedi, Teh-Ramgarh Shekhawati",
        "district": "Sikar",
        "state": "Rajasthan",
        "pin_code": "331024",
        "aadhar_no": "884632346886",
        "status": "Active",
        "admission_date": "2024-04-18",
        "is_online": False,
        "total_fee": 58500.0,
        "discount_amount": 0.0,
        "net_fee": 58500.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 2500.0, "paid_amount": 2500.0, "due_date": "2024-04-18", "payment_date": "2024-04-18", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 5000.0, "paid_amount": 5000.0, "due_date": "2024-05-19", "payment_date": "2024-05-19", "payment_mode": "Cash"},
            {"installment_no": 3, "installment_label": "3rd", "due_amount": 12000.0, "paid_amount": 12000.0, "due_date": "2025-03-18", "payment_date": "2025-03-18", "payment_mode": "Cash"},
            {"installment_no": 4, "installment_label": "4th", "due_amount": 7500.0, "paid_amount": 7500.0, "due_date": "2025-07-18", "payment_date": "2025-07-18", "payment_mode": "PhonePe"},
            {"installment_no": 5, "installment_label": "5th", "due_amount": 15000.0, "paid_amount": 0.0, "due_date": "2026-03-28", "payment_mode": "Cash"},
            {"installment_no": 6, "installment_label": "6th", "due_amount": 7000.0, "paid_amount": 0.0, "due_date": "2026-01-17", "payment_mode": "Cash"},
            {"installment_no": 7, "installment_label": "7th", "due_amount": 10000.0, "paid_amount": 0.0, "due_date": "2026-04-18", "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3075.png",
        "has_photo": True,
        "crop_box_ratios": [0.775, 0.188, 0.968, 0.372],
        "name": "Sachin Kumawat",
        "father_name": "Jugal Kishor",
        "mother_name": "Mangli Devi",
        "dob": "2005-08-21",
        "father_occupation": None,
        "college_school": "Shekhawati Institute of Engineering",
        "course_name": "Master",
        "year_sem": None,
        "mobile_no": "9928949043",
        "email": None,
        "father_contact_no": "9928949043",
        "alternate_contact_no": "9461639122",
        "permanent_address": "Ward No 12 Kumharo Ka Mohalla Mochiwara Sikar",
        "district": "Sikar",
        "state": "Rajasthan",
        "pin_code": "332001",
        "aadhar_no": "791821983357",
        "status": "Active",
        "admission_date": "2025-03-07",
        "is_online": False,
        "total_fee": 50000.0,
        "discount_amount": 0.0,
        "net_fee": 50000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2025-03-07", "payment_date": "2025-03-07", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2025-05-16", "payment_date": "2025-05-16", "payment_mode": "Cash"},
            {"installment_no": 3, "installment_label": "3rd", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2025-09-26", "payment_date": "2025-09-26", "payment_mode": "Cash"},
            {"installment_no": 4, "installment_label": "4th", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2025-10-13", "payment_date": "2025-10-13", "payment_mode": "Cash"},
            {"installment_no": 5, "installment_label": "5th", "due_amount": 10000.0, "paid_amount": 0.0, "due_date": "2026-01-06", "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3076.png",
        "has_photo": True,
        "crop_box_ratios": [0.785, 0.200, 0.980, 0.380],
        "name": "Radheshyam",
        "father_name": "Sera Ram Parjapat",
        "mother_name": "Chandrawali Devi",
        "dob": "1998-02-10",
        "father_occupation": None,
        "college_school": "M.G. Choudhary M.S. Memorial College",
        "course_name": "Master CAD",
        "year_sem": None,
        "mobile_no": "9414894938",
        "email": "radheshyamprajapat34@gmail.com",
        "father_contact_no": "9610695192",
        "alternate_contact_no": None,
        "permanent_address": "V. Mahatama, T. Taranagar",
        "district": "Churu",
        "state": "Rajasthan",
        "pin_code": "331304",
        "aadhar_no": "727309825628",
        "status": "Active",
        "admission_date": "2024-07-16",
        "is_online": False,
        "total_fee": 45000.0,
        "discount_amount": 0.0,
        "net_fee": 45000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 15000.0, "paid_amount": 15000.0, "due_date": "2024-07-16", "payment_date": "2024-07-16", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-11-30", "payment_date": "2024-11-30", "payment_mode": "Cash"},
            {"installment_no": 3, "installment_label": "3rd", "due_amount": 5000.0, "paid_amount": 5000.0, "due_date": "2025-03-12", "payment_date": "2025-03-12", "payment_mode": "Cash"},
            {"installment_no": 4, "installment_label": "4th", "due_amount": 5000.0, "paid_amount": 5000.0, "due_date": "2025-04-23", "payment_date": "2025-04-23", "payment_mode": "Cash"},
            {"installment_no": 5, "installment_label": "5th", "due_amount": 10000.0, "paid_amount": 0.0, "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3077.png",
        "has_photo": True,
        "crop_box_ratios": [0.785, 0.230, 0.980, 0.412],
        "name": "Mohit Parashar",
        "father_name": "Jagat Narayan",
        "mother_name": "Seema Devi",
        "dob": "2005-05-16",
        "father_occupation": None,
        "college_school": "College",
        "course_name": "CNC",
        "year_sem": "2025",
        "mobile_no": "7976103262",
        "email": "mparashar788@gmail.com",
        "father_contact_no": "9610703800",
        "alternate_contact_no": "9983761531 (Bro)",
        "permanent_address": "Mukundgarh",
        "district": "Jhunjhunu",
        "state": "Rajasthan",
        "pin_code": None,
        "aadhar_no": "938612451581",
        "status": "Active",
        "admission_date": "2025-07-09",
        "is_online": True,
        "online_reg_no": "CNC",
        "total_fee": 18000.0,
        "discount_amount": 0.0,
        "net_fee": 18000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 5000.0, "paid_amount": 5000.0, "due_date": "2025-07-09", "payment_date": "2025-07-09", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 5000.0, "paid_amount": 5000.0, "payment_mode": "PhonePe"},
            {"installment_no": 3, "installment_label": "3rd", "due_amount": 8000.0, "paid_amount": 0.0, "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3078.png",
        "has_photo": True,
        "crop_box_ratios": [0.765, 0.238, 0.955, 0.410],
        "name": "Anil Kumar Jangir",
        "father_name": "Bhanwar Lal Jangir",
        "mother_name": "Kamla Devi",
        "dob": "2002-11-11",
        "father_occupation": None,
        "college_school": "Govt. Sr. Secondary School, Kachwa",
        "course_name": "CNC Design",
        "year_sem": None,
        "mobile_no": "9828781202",
        "email": "aniljangid1202@gmail.com",
        "father_contact_no": "8955767984",
        "alternate_contact_no": None,
        "permanent_address": "Vill. Kachhwa, Post-Nechhwa, Dist. Sikar (Raj.)",
        "district": "Sikar",
        "state": "Rajasthan",
        "pin_code": "332026",
        "aadhar_no": "584979993783",
        "status": "Active",
        "admission_date": "2025-05-03",
        "is_online": True,
        "online_reg_no": "(CNC) Skep, Product Design",
        "total_fee": 34500.0,
        "discount_amount": 0.0,
        "net_fee": 34500.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 15000.0, "paid_amount": 15000.0, "due_date": "2025-05-03", "payment_date": "2025-05-03", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 19500.0, "paid_amount": 0.0, "due_date": "2026-01-31", "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3079.png",
        "has_photo": True,
        "crop_box_ratios": [0.770, 0.200, 0.965, 0.380],
        "name": "Faruk Mohammed Sahil",
        "father_name": "Faruk",
        "mother_name": "Farjana",
        "dob": "2002-10-18",
        "father_occupation": None,
        "college_school": "Pawar Shaheed Karnal JP Jan Shikshan Sansthan",
        "course_name": "AutoCAD / Master",
        "year_sem": None,
        "mobile_no": "8440827909",
        "email": "sk4704294@gmail.com",
        "father_contact_no": "9660604131",
        "alternate_contact_no": None,
        "permanent_address": "Millat Nagar, Ward No. 27, Jhunjhunu (Raj)",
        "district": "Jhunjhunu",
        "state": "Rajasthan",
        "pin_code": "333001",
        "aadhar_no": "341373177909",
        "status": "Active",
        "admission_date": "2023-11-08",
        "is_online": False,
        "total_fee": 70000.0,
        "discount_amount": 0.0,
        "net_fee": 70000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2023-11-08", "payment_date": "2023-11-08", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2023-12-26", "payment_date": "2023-12-26", "payment_mode": "Cash"},
            {"installment_no": 3, "installment_label": "3rd", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-04-30", "payment_date": "2024-04-30", "payment_mode": "Cash"},
            {"installment_no": 4, "installment_label": "4th", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-08-12", "payment_date": "2024-08-12", "payment_mode": "Cash"},
            {"installment_no": 5, "installment_label": "5th", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-12-11", "payment_date": "2024-12-11", "payment_mode": "Cash"},
            {"installment_no": 6, "installment_label": "6th", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2025-02-08", "payment_date": "2025-02-08", "payment_mode": "Cash"},
            {"installment_no": 7, "installment_label": "7th", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2025-05-07", "payment_date": "2025-05-07", "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3080.png",
        "has_photo": True,
        "crop_box_ratios": [0.758, 0.228, 0.948, 0.405],
        "name": "Irfan Khan",
        "father_name": "Rustam Khan",
        "mother_name": "Munni Bano",
        "dob": "2004-09-11",
        "father_occupation": "Saudi",
        "college_school": "Open Board",
        "course_name": "Architecture",
        "year_sem": "1st Year",
        "mobile_no": "9875234786",
        "email": "ikking112004@gmail.com",
        "father_contact_no": "9875234786",
        "alternate_contact_no": "7229960312 (Mother)",
        "permanent_address": "Beri Khunkhuna",
        "district": "Nagaur",
        "state": "Rajasthan",
        "pin_code": "341318",
        "aadhar_no": "247629464334",
        "status": "Active",
        "admission_date": "2023-09-12",
        "is_online": True,
        "online_reg_no": "Bhadra Master 29/02",
        "total_fee": 45000.0,
        "discount_amount": 0.0,
        "net_fee": 45000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2023-09-12", "payment_date": "2023-09-12", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2023-10-03", "payment_date": "2023-10-03", "payment_mode": "Cash"},
            {"installment_no": 3, "installment_label": "3rd", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-04-26", "payment_date": "2024-04-26", "payment_mode": "Cash"},
            {"installment_no": 4, "installment_label": "4th", "due_amount": 15000.0, "paid_amount": 0.0, "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3081.png",
        "has_photo": True,
        "crop_box_ratios": [0.792, 0.188, 0.985, 0.378],
        "name": "Gautam Saini",
        "father_name": "Surendra Saini",
        "mother_name": "Priya Saini",
        "dob": "2005-08-20",
        "father_occupation": "Contractor",
        "college_school": "Shri Radheshyam R. Morarka College",
        "course_name": "CAD / Architecture",
        "year_sem": None,
        "mobile_no": "9680355572",
        "email": "gautamsaini27118@gmail.com",
        "father_contact_no": "7733935572",
        "alternate_contact_no": "9680355572",
        "permanent_address": "Sikar",
        "district": "Sikar",
        "state": "Rajasthan",
        "pin_code": None,
        "aadhar_no": None,
        "status": "Active",
        "admission_date": "2024-07-08",
        "is_online": False,
        "total_fee": 59000.0,
        "discount_amount": 0.0,
        "net_fee": 59000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 35000.0, "paid_amount": 35000.0, "due_date": "2024-07-08", "payment_date": "2024-07-08", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 5000.0, "paid_amount": 5000.0, "due_date": "2024-09-13", "payment_date": "2024-09-13", "payment_mode": "Cash"},
            {"installment_no": 3, "installment_label": "3rd", "due_amount": 12000.0, "paid_amount": 12000.0, "due_date": "2025-09-27", "payment_date": "2025-09-27", "payment_mode": "Cash"},
            {"installment_no": 4, "installment_label": "4th", "due_amount": 7000.0, "paid_amount": 0.0, "remarks": "Sikar", "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3082.png",
        "has_photo": True,
        "crop_box_ratios": [0.758, 0.215, 0.942, 0.380],
        "name": "Ankit Jangir",
        "father_name": "Shiv Bhagwan Jangir",
        "mother_name": "Teeju Devi",
        "dob": "2001-11-15",
        "father_occupation": None,
        "college_school": "Shekhawati Pub. School Losal",
        "course_name": "Commerce / CAD",
        "year_sem": "2018",
        "mobile_no": "7891782145",
        "email": "ankitjangir2145@gmail.com",
        "father_contact_no": "9983604705",
        "alternate_contact_no": "7891635569",
        "permanent_address": "Ward No. 5 Maliyon Ki Dhani Bheerian",
        "district": "Sikar",
        "state": "Rajasthan",
        "pin_code": "332025",
        "aadhar_no": "453974735882",
        "status": "Completed",
        "admission_date": "2024-02-29",
        "is_online": True,
        "online_reg_no": "C02303232415859",
        "total_fee": 60000.0,
        "discount_amount": 0.0,
        "net_fee": 60000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-02-29", "payment_date": "2024-02-29", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 25000.0, "paid_amount": 25000.0, "due_date": "2024-03-12", "payment_date": "2024-03-12", "payment_mode": "Cash"},
            {"installment_no": 3, "installment_label": "3rd", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-07-02", "payment_date": "2024-07-02", "payment_mode": "Cash"},
            {"installment_no": 4, "installment_label": "4th", "due_amount": 5000.0, "paid_amount": 5000.0, "due_date": "2025-03-17", "payment_date": "2025-03-17", "payment_mode": "Cash"},
            {"installment_no": 5, "installment_label": "5th", "due_amount": 5000.0, "paid_amount": 5000.0, "due_date": "2026-05-12", "payment_date": "2026-05-12", "payment_mode": "Cash"},
            {"installment_no": 6, "installment_label": "6th", "due_amount": 5000.0, "paid_amount": 5000.0, "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3083.png",
        "has_photo": True,
        "crop_box_ratios": [0.770, 0.228, 0.958, 0.400],
        "name": "Ankur Sharma",
        "father_name": "Vinod Kumar Sharma",
        "mother_name": "Kishori Devi",
        "dob": "2002-05-28",
        "father_occupation": "Seller (Medical shop)",
        "college_school": "Gyan Sindhu",
        "course_name": "Master Architect",
        "year_sem": None,
        "mobile_no": "8000956360",
        "email": "ankurbagri26@gmail.com",
        "father_contact_no": "8107625827",
        "alternate_contact_no": "9680807280",
        "permanent_address": "Chirawa",
        "district": "Jhunjhunu",
        "state": "Rajasthan",
        "pin_code": "333026",
        "aadhar_no": "777233436091",
        "status": "Active",
        "admission_date": "2024-06-26",
        "is_online": True,
        "online_reg_no": "31 Dec 25",
        "total_fee": 66000.0,
        "discount_amount": 0.0,
        "net_fee": 66000.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-06-26", "payment_date": "2024-06-26", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 10000.0, "paid_amount": 10000.0, "due_date": "2024-08-05", "payment_date": "2024-08-05", "payment_mode": "Cash"},
            {"installment_no": 3, "installment_label": "3rd", "due_amount": 15000.0, "paid_amount": 15000.0, "due_date": "2024-09-06", "payment_date": "2024-09-06", "payment_mode": "Cash"},
            {"installment_no": 4, "installment_label": "4th", "due_amount": 5000.0, "paid_amount": 5000.0, "due_date": "2025-01-15", "payment_date": "2025-01-15", "payment_mode": "Cash"},
            {"installment_no": 5, "installment_label": "5th", "due_amount": 5000.0, "paid_amount": 5000.0, "due_date": "2025-03-04", "payment_date": "2025-03-04", "payment_mode": "Cash"},
            {"installment_no": 6, "installment_label": "6th", "due_amount": 5000.0, "paid_amount": 5000.0, "due_date": "2025-05-05", "payment_date": "2025-05-05", "payment_mode": "Cash"},
            {"installment_no": 7, "installment_label": "7th", "due_amount": 3000.0, "paid_amount": 3000.0, "due_date": "2025-08-18", "payment_date": "2025-08-18", "payment_mode": "Cash"},
            {"installment_no": 8, "installment_label": "8th", "due_amount": 5000.0, "paid_amount": 5000.0, "due_date": "2025-10-02", "payment_date": "2025-10-02", "payment_mode": "Cash"},
            {"installment_no": 9, "installment_label": "9th", "due_amount": 3000.0, "paid_amount": 3000.0, "due_date": "2025-12-30", "payment_date": "2025-12-30", "payment_mode": "Cash"},
            {"installment_no": 10, "installment_label": "10th", "due_amount": 5000.0, "paid_amount": 0.0, "due_date": "2026-01-08", "payment_mode": "Cash"},
        ]
    },
    {
        "source_image": "IMG_3084.png",
        "has_photo": True,
        "crop_box_ratios": [0.772, 0.235, 0.952, 0.395],
        "name": "Jaya Prakash Jangir",
        "father_name": "Girdhari Lal Jangir",
        "mother_name": "Vinod Jangir",
        "dob": "1993-07-17",
        "father_occupation": None,
        "college_school": "Seth G.R. Fatehpur",
        "course_name": "CAD Detailing",
        "year_sem": None,
        "mobile_no": "9636757683",
        "email": "jayprakashjangid81@gmail.com",
        "father_contact_no": "9460256009",
        "alternate_contact_no": None,
        "permanent_address": "V.P.O Kayam Sar, Jangir Colony, Teh. Ramgarh Shekhawati",
        "district": "Sikar",
        "state": "Rajasthan",
        "pin_code": "331024",
        "aadhar_no": "667551248294",
        "status": "Active",
        "admission_date": "2024-06-24",
        "is_online": True,
        "online_reg_no": "31/07/24",
        "total_fee": 57500.0,
        "discount_amount": 0.0,
        "net_fee": 57500.0,
        "installments": [
            {"installment_no": 1, "installment_label": "1st", "due_amount": 20000.0, "paid_amount": 20000.0, "due_date": "2024-06-24", "payment_date": "2024-06-24", "payment_mode": "Cash"},
            {"installment_no": 2, "installment_label": "2nd", "due_amount": 18000.0, "paid_amount": 18000.0, "due_date": "2024-11-28", "payment_date": "2024-11-28", "payment_mode": "Cash"},
            {"installment_no": 3, "installment_label": "3rd", "due_amount": 9500.0, "paid_amount": 9500.0, "due_date": "2024-11-28", "payment_date": "2024-11-28", "payment_mode": "Cash"},
            {"installment_no": 4, "installment_label": "4th", "due_amount": 5000.0, "paid_amount": 5000.0, "due_date": "2025-01-21", "payment_date": "2025-01-21", "payment_mode": "Cash"},
            {"installment_no": 5, "installment_label": "5th", "due_amount": 5000.0, "paid_amount": 0.0, "payment_mode": "Cash"},
        ]
    }
]

def parse_date(d_str):
    if not d_str:
        return None
    try:
        return datetime.strptime(d_str, "%Y-%m-%d").date()
    except Exception:
        return None

def compute_running_installments(net_fee: float, raw_installments: list) -> list:
    computed = []
    running_due = float(net_fee)
    for idx, inst in enumerate(raw_installments):
        paid_amt = float(inst.get("paid_amount") or 0.0)

        # Determine running due for this row
        if paid_amt > 0 or idx == 0:
            cur_due = running_due
        elif running_due > 0 and idx > 0 and (float(raw_installments[idx - 1].get("paid_amount") or 0.0) > 0):
            cur_due = running_due
        elif inst.get("due_amount") is not None and float(inst.get("due_amount") or 0.0) > 0:
            cur_due = float(inst.get("due_amount"))
        else:
            cur_due = 0.0

        # Status
        if paid_amt > 0:
            st = "Paid"
        elif cur_due > 0:
            st = "Pending"
        else:
            st = "Pending"

        inst_dict = dict(inst)
        inst_dict["due_amount"] = cur_due
        inst_dict["status"] = st
        computed.append(inst_dict)

        running_due = max(0.0, running_due - paid_amt)
    return computed


def main():
    print("=== Personal CRM Admission Importer & Photo Cropper ===")
    init_db()

    images_dir = DATA_DIR / "data images"
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

    imported_students_json = []

    for idx, item in enumerate(RAW_STUDENTS_DATA, start=1):
        id_no = f"CD-2026-{idx:04d}"
        photo_filename = None

        # 1. Crop Photo if present
        if item.get("has_photo"):
            src_img_path = images_dir / item["source_image"]
            if src_img_path.exists():
                try:
                    with Image.open(src_img_path) as img:
                        w, h = img.size
                        r = item["crop_box_ratios"]
                        crop_box = (
                            int(w * r[0]),
                            int(h * r[1]),
                            int(w * r[2]),
                            int(h * r[3]),
                        )
                        cropped = img.crop(crop_box)
                        
                        # Save photo
                        photo_filename = f"photo_{id_no.replace('/', '_')}.jpg"
                        dest_photo_path = PHOTOS_DIR / photo_filename
                        cropped.convert("RGB").save(str(dest_photo_path), "JPEG", quality=92)
                        print(f"[{idx}/28] Cropped photo for {item['name']} -> {photo_filename}")
                except Exception as e:
                    print(f"Error cropping photo for {item['name']}: {e}")

        # Compute running due installments
        computed_installments = compute_running_installments(item["net_fee"], item["installments"])

        # 2. Structure student entry for JSON
        student_entry = {
            "id_no": id_no,
            "name": item["name"],
            "father_name": item.get("father_name"),
            "mother_name": item.get("mother_name"),
            "dob": item.get("dob"),
            "father_occupation": item.get("father_occupation"),
            "college_school": item.get("college_school"),
            "course_name": item.get("course_name"),
            "year_sem": item.get("year_sem"),
            "mobile_no": item["mobile_no"],
            "email": item.get("email"),
            "father_contact_no": item.get("father_contact_no"),
            "alternate_contact_no": item.get("alternate_contact_no"),
            "permanent_address": item.get("permanent_address"),
            "district": item.get("district"),
            "state": item.get("state"),
            "pin_code": item.get("pin_code"),
            "aadhar_no": item.get("aadhar_no"),
            "status": item.get("status", "Active"),
            "admission_date": item.get("admission_date"),
            "is_online": item.get("is_online", False),
            "online_reg_no": item.get("online_reg_no"),
            "photo_path": photo_filename,
            "total_fee": item["total_fee"],
            "discount_amount": item["discount_amount"],
            "net_fee": item["net_fee"],
            "installments": computed_installments,
            "source_image": item["source_image"],
        }
        imported_students_json.append(student_entry)

        # 3. Save into SQLite Database
        with get_db_session() as session:
            # Check if student already exists by mobile_no or id_no
            existing = session.query(Student).filter(
                (Student.id_no == id_no) | (Student.mobile_no == item["mobile_no"])
            ).first()

            if existing:
                student = existing
                student.name = item["name"]
                student.father_name = item.get("father_name")
                student.mother_name = item.get("mother_name")
                student.dob = parse_date(item.get("dob"))
                student.father_occupation = item.get("father_occupation")
                student.college_school = item.get("college_school")
                student.course_name = item.get("course_name")
                student.year_sem = item.get("year_sem")
                student.mobile_no = item["mobile_no"]
                student.email = item.get("email")
                student.father_contact_no = item.get("father_contact_no")
                student.alternate_contact_no = item.get("alternate_contact_no")
                student.permanent_address = item.get("permanent_address")
                student.district = item.get("district")
                student.state = item.get("state")
                student.pin_code = item.get("pin_code")
                student.aadhar_no = item.get("aadhar_no")
                student.status = item.get("status", "Active")
                student.admission_date = parse_date(item.get("admission_date")) or date.today()
                student.is_online = item.get("is_online", False)
                student.online_reg_no = item.get("online_reg_no")
                if photo_filename:
                    student.photo_path = photo_filename
                student.total_fee = item["total_fee"]
                student.discount_amount = item["discount_amount"]
                student.net_fee = item["net_fee"]

                # Clear old installments and re-add
                session.query(StudentFeeInstallment).filter(StudentFeeInstallment.student_id == student.id).delete()
            else:
                student = Student(
                    id_no=id_no,
                    name=item["name"],
                    father_name=item.get("father_name"),
                    mother_name=item.get("mother_name"),
                    dob=parse_date(item.get("dob")),
                    father_occupation=item.get("father_occupation"),
                    college_school=item.get("college_school"),
                    course_name=item.get("course_name"),
                    year_sem=item.get("year_sem"),
                    mobile_no=item["mobile_no"],
                    email=item.get("email"),
                    father_contact_no=item.get("father_contact_no"),
                    alternate_contact_no=item.get("alternate_contact_no"),
                    permanent_address=item.get("permanent_address"),
                    district=item.get("district"),
                    state=item.get("state"),
                    pin_code=item.get("pin_code"),
                    aadhar_no=item.get("aadhar_no"),
                    status=item.get("status", "Active"),
                    admission_date=parse_date(item.get("admission_date")) or date.today(),
                    is_online=item.get("is_online", False),
                    online_reg_no=item.get("online_reg_no"),
                    photo_path=photo_filename,
                    total_fee=item["total_fee"],
                    discount_amount=item["discount_amount"],
                    net_fee=item["net_fee"],
                )
                session.add(student)
                session.flush()

            # Add Installments
            for inst in computed_installments:
                due_amt = float(inst.get("due_amount", 0.0))
                paid_amt = float(inst.get("paid_amount", 0.0))
                st = inst.get("status", "Paid" if paid_amt > 0 else "Pending")

                inst_obj = StudentFeeInstallment(
                    student_id=student.id,
                    installment_no=inst["installment_no"],
                    installment_label=inst["installment_label"],
                    due_amount=due_amt,
                    paid_amount=paid_amt,
                    due_date=parse_date(inst.get("due_date")),
                    payment_date=parse_date(inst.get("payment_date")),
                    payment_mode=inst.get("payment_mode", "Cash"),
                    remarks=inst.get("remarks"),
                    status=st,
                )
                session.add(inst_obj)

            session.commit()
            print(f"-> Saved database record: {id_no} - {student.name}")

    # 4. Save to JSON File
    json_path = DATA_DIR / "students_extracted_data.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(imported_students_json, f, indent=2, ensure_ascii=False)
    print(f"\n[SUCCESS] Extracted JSON saved to: {json_path}")
    print(f"Total students processed: {len(imported_students_json)}")

if __name__ == "__main__":
    main()
