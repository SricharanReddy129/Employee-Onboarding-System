-- =========================================================
-- 1. Offer Letter Details
-- =========================================================
CREATE TABLE offer_letter_details (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    user_uuid BINARY(16) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    mail VARCHAR(100) NOT NULL UNIQUE,
    country_code VARCHAR(5) NOT NULL, 
    contact_number VARCHAR(15) NOT NULL,
    designation VARCHAR(50) NOT NULL,
    package VARCHAR(20) NOT NULL,
    status ENUM('Offered', 'Accepted', 'Rejected') DEFAULT 'Offered',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =========================================================
-- 2. Countries Master
-- =========================================================
CREATE TABLE countries (
    country_id INT PRIMARY KEY AUTO_INCREMENT,
    country_uuid BINARY(16) NOT NULL UNIQUE,
    country_name VARCHAR(100) NOT NULL,
    calling_code VARCHAR(5),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =========================================================
-- 3. Contact Details
-- =========================================================
CREATE TABLE contacts (
    contact_id INT PRIMARY KEY AUTO_INCREMENT,
    contact_uuid BINARY(16) NOT NULL UNIQUE,
    user_uuid BINARY(16) NOT NULL,
    country_uuid BINARY(16) NOT NULL,
    contact_number VARCHAR(15) NOT NULL,
    emergency_contact VARCHAR(15) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_uuid) REFERENCES offer_letter_details(user_uuid),
    FOREIGN KEY (country_uuid) REFERENCES countries(country_uuid)
);

-- =========================================================
-- 4. Personal Details
-- =========================================================
CREATE TABLE personal_details (
    id INT PRIMARY KEY AUTO_INCREMENT,
    personal_uuid BINARY(16) NOT NULL UNIQUE,
    user_uuid BINARY(16) NOT NULL,
    date_of_birth DATE,
    gender ENUM('Male', 'Female', 'Other'),
    marital_status ENUM('Single', 'Married', 'Divorced', 'Widowed'),
    blood_group VARCHAR(5),
    nationality_country_uuid BINARY(16),
    residence_country_uuid BINARY(16),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_uuid) REFERENCES offer_letter_details(user_uuid),
    FOREIGN KEY (nationality_country_uuid) REFERENCES countries(country_uuid),
    FOREIGN KEY (residence_country_uuid) REFERENCES countries(country_uuid)
);

-- =========================================================
-- 5. Permanent Address Details
-- =========================================================
CREATE TABLE permanent_addresses (
    address_id INT PRIMARY KEY AUTO_INCREMENT,
    address_uuid BINARY(16) NOT NULL UNIQUE,
    user_uuid BINARY(16) NOT NULL,
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    country_uuid BINARY(16),
    postal_code VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_uuid) REFERENCES offer_letter_details(user_uuid),
    FOREIGN KEY (country_uuid) REFERENCES countries(country_uuid)
);

-- =========================================================
-- 6. Current Address Details
-- =========================================================
CREATE TABLE current_addresses (
    address_id INT PRIMARY KEY AUTO_INCREMENT,
    address_uuid BINARY(16) NOT NULL UNIQUE,
    user_uuid BINARY(16) NOT NULL,
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    country_uuid BINARY(16),
    postal_code VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_uuid) REFERENCES offer_letter_details(user_uuid),
    FOREIGN KEY (country_uuid) REFERENCES countries(country_uuid)
);

-- =========================================================
-- 7. Identity Type Master
-- =========================================================
CREATE TABLE identity_type (
    identity_type_id INT PRIMARY KEY AUTO_INCREMENT,
    identity_type_uuid BINARY(16) NOT NULL UNIQUE,
    identity_type_name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =========================================================
-- 8. Country–Identity Mapping
-- =========================================================
CREATE TABLE country_identity_mapping (
    mapping_id INT PRIMARY KEY AUTO_INCREMENT,
    mapping_uuid BINARY(16) NOT NULL UNIQUE,
    country_uuid BINARY(16) NOT NULL,
    identity_type_uuid BINARY(16) NOT NULL,
    is_mandatory BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (country_uuid) REFERENCES countries(country_uuid),
    FOREIGN KEY (identity_type_uuid) REFERENCES identity_type(identity_type_uuid)
);

-- =========================================================
-- 9. Employee Identity Document Uploads
-- =========================================================
CREATE TABLE employee_identity_document (
    employee_identity_document_id INT PRIMARY KEY AUTO_INCREMENT,
    document_uuid BINARY(16) NOT NULL UNIQUE,
    mapping_uuid BINARY(16) NOT NULL,
    user_uuid BINARY(16) NOT NULL,
    file_path VARCHAR(255),
    expiry_date DATE,
    status ENUM('uploaded', 'pending', 'verified', 'rejected') DEFAULT 'pending',
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    verified_by BINARY(16) NULL,
    verified_at DATETIME NULL,
    remarks VARCHAR(255),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (mapping_uuid) REFERENCES country_identity_mapping(mapping_uuid),
    FOREIGN KEY (user_uuid) REFERENCES offer_letter_details(user_uuid)
);

-- =========================================================
-- 10. Education Level Master
-- =========================================================
CREATE TABLE education_level (
    education_id INT PRIMARY KEY AUTO_INCREMENT,
    education_uuid BINARY(16) NOT NULL UNIQUE,
    education_name VARCHAR(100) NOT NULL,
    description VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =========================================================
-- 11. Education Document Type Master
-- =========================================================
CREATE TABLE education_document_type (
    education_document_id INT PRIMARY KEY AUTO_INCREMENT,
    education_document_uuid BINARY(16) NOT NULL UNIQUE,
    document_name VARCHAR(100) NOT NULL,
    description VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- 12. Country–Education–Document Mapping
-- =========================================================
CREATE TABLE country_education_document_mapping (
    mapping_id INT PRIMARY KEY AUTO_INCREMENT,
    mapping_uuid BINARY(16) NOT NULL UNIQUE,
    country_uuid BINARY(16) NOT NULL,
    education_uuid BINARY(16) NOT NULL,
    education_document_uuid BINARY(16) NOT NULL,
    is_mandatory BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (country_uuid) REFERENCES countries(country_uuid),
    FOREIGN KEY (education_uuid) REFERENCES education_level(education_uuid),
    FOREIGN KEY (education_document_uuid) REFERENCES education_document_type(education_document_uuid)
);

-- =========================================================
-- 13. Employee Education Document Uploads
-- =========================================================
CREATE TABLE employee_education_document (
    employee_education_document_id INT PRIMARY KEY AUTO_INCREMENT,
    document_uuid BINARY(16) NOT NULL UNIQUE,
    mapping_uuid BINARY(16) NOT NULL,
    user_uuid BINARY(16) NOT NULL,
    institution_name VARCHAR(150),
    specialization VARCHAR(150),
    year_of_passing YEAR,
    file_path VARCHAR(255),
    status ENUM('uploaded', 'pending', 'verified', 'rejected') DEFAULT 'pending',
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    verified_by BINARY(16) NULL,
    verified_at DATETIME NULL,
    remarks VARCHAR(255),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (mapping_uuid) REFERENCES country_education_document_mapping(mapping_uuid),
    FOREIGN KEY (user_uuid) REFERENCES offer_letter_details(user_uuid)
);

-- =========================================================
-- 14. Employee Experience Details
-- =========================================================
CREATE TABLE employee_experience (
    experience_id INT PRIMARY KEY AUTO_INCREMENT,
    experience_uuid BINARY(16) NOT NULL UNIQUE,
    employee_uuid BINARY(16) NOT NULL,
    company_name VARCHAR(150) NOT NULL,
    role_title VARCHAR(100),
    employment_type ENUM('Full-Time', 'Part-Time', 'Intern', 'Contract', 'Freelance'),
    start_date DATE NOT NULL,
    end_date DATE NULL,
    is_current BOOLEAN DEFAULT FALSE,
    exp_certificate_path VARCHAR(255),
    certificate_status ENUM('uploaded', 'pending', 'verified', 'rejected') DEFAULT 'pending',
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    verified_by BINARY(16) NULL,
    verified_at DATETIME NULL,
    remarks VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_uuid) REFERENCES offer_letter_details(user_uuid)
);

-- =========================================================
-- 15. Employee Pay Slips (Only for Last Company)
-- =========================================================
CREATE TABLE employee_pay_slips (
    pay_slip_id INT PRIMARY KEY AUTO_INCREMENT,
    pay_slip_uuid BINARY(16) NOT NULL UNIQUE,
    employee_uuid BINARY(16) NOT NULL,
    experience_uuid BINARY(16) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    status ENUM('uploaded', 'pending', 'verified', 'rejected') DEFAULT 'pending',
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    verified_by BINARY(16) NULL,
    verified_at DATETIME NULL,
    remarks VARCHAR(255),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_uuid) REFERENCES offer_letter_details(user_uuid),
    FOREIGN KEY (experience_uuid) REFERENCES employee_experience(experience_uuid)
);

-- =========================================================
-- 16. Employee Relieving Letter (Submitted on Joining Day)
-- =========================================================
CREATE TABLE employee_relieving_letter (
    relieving_id INT PRIMARY KEY AUTO_INCREMENT,
    relieving_uuid BINARY(16) NOT NULL UNIQUE,
    employee_uuid BINARY(16) NOT NULL,
    experience_uuid BINARY(16) NOT NULL,
    file_path VARCHAR(255),
    status ENUM('uploaded', 'pending', 'verified', 'rejected') DEFAULT 'pending',
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    verified_by BINARY(16) NULL,
    verified_at DATETIME NULL,
    remarks VARCHAR(255),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_uuid) REFERENCES offer_letter_details(user_uuid),
    FOREIGN KEY (experience_uuid) REFERENCES employee_experience(experience_uuid)
);

-- =========================================================
-- 17. Deliverable Master
-- =========================================================
CREATE TABLE deliverable_items (
    deliverable_id INT PRIMARY KEY AUTO_INCREMENT,
    deliverable_uuid BINARY(16) NOT NULL UNIQUE,
    item_name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- 18. Employee Deliverables
-- =========================================================
CREATE TABLE employee_deliverables (
    employee_deliverable_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_deliverable_uuid BINARY(16) NOT NULL UNIQUE,
    user_uuid BINARY(16) NOT NULL,
    deliverable_uuid BINARY(16) NOT NULL,
    status ENUM('Pending', 'Delivered', 'Returned') DEFAULT 'Pending',
    issued_by BINARY(16) NULL,
    issued_at DATETIME NULL,
    returned_at DATETIME NULL,
    remarks VARCHAR(255),
    FOREIGN KEY (user_uuid) REFERENCES offer_letter_details(user_uuid),
    FOREIGN KEY (deliverable_uuid) REFERENCES deliverable_items(deliverable_uuid)
);

-- =========================================================
-- 19. Receivable Master
-- =========================================================
CREATE TABLE receivable_items (
    receivable_id INT PRIMARY KEY AUTO_INCREMENT,
    receivable_uuid BINARY(16) NOT NULL UNIQUE,
    item_name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- 20. Employee Receivables
-- =========================================================
CREATE TABLE employee_receivables (
    employee_receivable_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_receivable_uuid BINARY(16) NOT NULL UNIQUE,
    user_uuid BINARY(16) NOT NULL,
    receivable_uuid BINARY(16) NOT NULL,
    status ENUM('Pending', 'Received', 'Not Received') DEFAULT 'Pending',
    collected_by BINARY(16) NULL,
    collected_at DATETIME NULL,
    remarks VARCHAR(255),
    FOREIGN KEY (user_uuid) REFERENCES offer_letter_details(user_uuid),
    FOREIGN KEY (receivable_uuid) REFERENCES receivable_items(receivable_uuid)
);
