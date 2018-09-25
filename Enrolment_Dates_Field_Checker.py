# Enrolment Dates Field Checker
# Version 0.1 25 September 2018
# Created by Jeff Mitchell
# Check that the enrolment dates on student profiles match their enrolment
# dates in the Learning Platform

# Data sources:

# Enrolment Dates query from Learning Platform
# Custom Fields query from Learning Platform

import csv
import re
import sys
import time


def add_end_date(students, data_pos):
    """Add End Date to each student's data.
    
    Finds the End Date in the data column and then appends this to the
    student's data and returns an updated list.
    
    Args:
        students (list): Student data.
        data_pos (int): Position of data column to be checked.
    
    Returns:
        updated_students (list): List of students with End Date appended.
    """
    updated_students = list(students)
    text = 'Course End Date'
    for student in updated_students:
        end_date = extract_course_date(student, data_pos, text)
        student.append(end_date)
    return updated_students


def add_start_date(students, data_pos):
    """Add Start Date to each student's data.
    
    Finds the Start Date in the data column and then appends this to the
    student's data and returns an updated list.
    
    Args:
        students (list): Student data.
        data_pos (int): Position of data column to be checked.
    
    Returns:
        updated_students (list): List of students with Start Date appended.
    """
    updated_students = list(students)
    text = 'Course Start Date'
    for student in updated_students:
        start_date = extract_course_date(student, data_pos, text)
        student.append(start_date)
    return updated_students


def add_student_id(students, data_pos):
    """Add Student ID to each student's data.
    
    Finds the Student ID in the data column and then appends this to the
    student's data and returns an updated list.
    
    Args:
        students (list): Student data.
        data_pos (int): Position of data column to be checked.
    
    Returns:
        updated_students (list): List of students with 'FitNZ'.
    """
    updated_students = list(students)
    for student in updated_students:
        student_id = extract_student_id(student, data_pos)
        student.append(student_id)
    return updated_students


def check_ed(report_data):
    """Check the data in the Enrolment Dates (Learning Platform) data file.
    
    Checks the Enrolment Dates (Learning Platform) report data to see if the 
    required information is present. Missing or incorrect information that is 
    non-fatal is appended to a warnings list and returned.

    Args:
        report_data (list): Enrolment Dates (Learning Platform) data file

    Returns:
        True if warnings list has had items appended to it, False otherwise.
        warnings (list): Warnings that have been identified in the data.

    File Structure (Enrolment Dates (Learning Platform) data file):
        Student ID, Student, Course, Enrolment Date, Expiry Date
        
    File Source(Enrolment Dates (Learning Platform) data file):
        Enrolment Dates database query in the Learning Platform.
    """
    errors = []
    i = 0
    warnings = ['\nEnrolment Dates (Learning Platform) Report Warnings:\n']
    while i < len(report_data):
        student = report_data[i]
        if student[1] in (None, ''):
            warnings.append('Student Name is missing for student with '
                            'Student ID {}'.format(student[0]))
        if student[2] in (None, ''):
            errors.append('Course is missing for student with Student ID'
                          ' {}'.format(student[0]))
        if student[3] in (None, ''):
            errors.append('Enrolment Date is missing for student with Student '
                            'ID {}'.format(student[0]))
        if student[4] in (None, ''):
            errors.append('Expiry Date is missing for student with Student '
                            'ID {}'.format(student[0]))
        i += 1
    # Check if any errors have been identified, save error log if they have
    if len(errors) > 0:
        process_error_log(errors, 'Enrolment Dates (Learning Platform) Report')
    # Check if any warnings have been identified, save error log if they have
    if len(warnings) > 1:
        return True, warnings
    else:
        return False, warnings


def check_repeat():
    """Return True or False for repeating another action.

    Returns:
        True if user wants to perform another action, False otherwise.
    """
    repeat = ''
    while repeat == '':
        repeat = input("\nDo you want to prepare another file? y/n --> ")
        if repeat != 'y' and repeat != 'n':
            print("\nThat is not a valid answer! Please try again.")
            repeat = ''
        elif repeat == 'y':
            return True
        else:
            return False


def check_review_warnings():
    """Return True or False for reviewing warning messages.

    Returns:
        True if user wants to review warning messages, False otherwise.
    """
    review = ''
    while review == '':
        review = input('\nDo you want to view the warning messages? y/n --> ')
        if review not in ('y', 'n'):
            print('\nThat is not a valid answer! Please try again.')
            review = ''
        elif review == 'y':
            return True
        else:
            return False


def clean_date(students, date_pos):
    """Returns list with the date column converted to 'DD/MM/YYYY'.
    
    Args:
        students (list): Student data.
        date_pos (int): Position of date column to be cleaned.
    
    Returns:
        updated_students (list): Student data with date column cleaned.
    """
    updated_students = []
    for student in students:
        student[date_pos] = extract_date(student[date_pos])
        updated_students.append(student)
    return updated_students


def compare(enrolment, custom_field, e_pos, c_pos, es_pos=0, cs_pos=0):
    """Compare dates to find those that are incorrect in Custom Fields.
    
    Compares dates between the enrolment data and the custom fields data.
        
    Args:
        enrolment (list): Enrolment Dates data.
        custom_field (list): Custom Fields data.
        e_pos (int): Position of date in Enrolment Dates data.
        c_pos (int): Position of date in Custom Fields data.
        es_pos (int): Position of Student ID in Enrolment Dates data.
        cs_pos (int): Position of Student ID in Custom Fields data.
    
    Returns:
        changes (list): Students needing changing and correct date.
    """
    changes = []
    for student in enrolment:
        for c_student in custom_field:
            # Find matching Student ID Numbers
            if student[es_pos] == c_student[cs_pos]:
                # Compare dates for student
                if student[e_pos] != c_student[c_pos]:
                    changed_student = [student[es_pos], student[e_pos]]
                    changes.append(changed_student)
                    break
                else:
                    break
    return changes


def confirm_files(o_file, r_files):
    """Print required files and have user press enter to continue.

    Args:
        o_file (str): Name of file that is being processed.
        r_files (list): List of files that need to be present.
    """
    num_files = len(r_files)
    if num_files == 1:
        text_f = 'this file is'
    else:
        text_f = 'these files are'
    print('\nTo process the {} the following files are required:\n'.format
          (o_file))
    for file in r_files:
        print(file)
    print('\nPlease make sure that {} in the required folder and are updated '
          'correctly before proceeding.'.format(text_f))
    input('\nPress the enter key to continue processing the {} file '
          '--> '.format(o_file))


def debug_dict(test_dict):
    """Print out contents of a dictionary.

    Args:
        test_dict (dict): Dictionary to be printed out.
    """
    i = 0
    for k, v in test_dict.items():
        print(k, v)
        i += 1


def debug_list(test_list):
    """Print out contents of a list.

    Args:
        test_list (listt): List to be printed out.
    """
    i = 0
    while i < len(test_list):
        print('Item ' + str(i))
        print(str(test_list[i]))
        i += 1


def debug_list_item(test_item):
    """Print out a single list item.

    Args:
    test_item (string): Item to be printed.
    """
    print(test_item)


def extract_course_code(course):
    """Extract the course code.
    
    Looks for the course code in a course string (XXX-XX-XXX). If it is present
    it returns the course code. If it is not present it returns 'Skip'.
    
    Args:
        course (str): Full course name to be searched.
    
    Returns:
        Either the course code or 'Skip' if a course code cannot be found.
    """
    if re.search('.+\(.+-.+-.+\)', course):
        # Extract the course code and return it
        start = course.index('(')
        return course[start+1:-1]
    else:
        return 'Skip'


def extract_course_date(student, data_pos, date_text):
    """Return the student's Course Date in the format DD/MM/YYYY.
    
    Finds the Course Date by searching in the string for date_text value,
    finding the first digit following this, extracting the Course Date and
    returning it in the format DD/MM/YYYY.
    
    Args:
        student (list): Individual student data.
        data_pos (int): Position of data column to be processed.
        date_text (str): Text to search for to identify date. Should be
        immediately before the date in the data.
    
    Returns:
        course_date (str): Extracted Course Date.
    """
    # Find the start of the course date text
    date_text = student[data_pos].find(date_text)
    # Find the start of the date - the first number after date_text
    remaining = student[data_pos][date_text:]
    m = re.search('\d', remaining)
    date_start = m.start()
    # Get text from start of date to end of string
    date_remaining = remaining[date_start:]
    # Find the first '/' and capture the day component
    first_slash = date_remaining.find('/')
    day = date_remaining[:first_slash]
    # Find second slash and capture the month component
    date_remaining_month = date_remaining[first_slash+1:]
    second_slash = date_remaining_month.find('/')
    month = date_remaining_month[:second_slash]
    # Extract year - four characters after second slash
    year = date_remaining_month[second_slash+1:second_slash+5]
    course_date = day + '/' + month + '/' + year
    # print('Debugging: Course Date: {}: {}'.format(student[5], course_date))
    return course_date


def extract_date(date):
    """Return the date in the format DD/MM/YYYY.
    
    Replaces the provided date with one in the format DD/MM/YYYY. The separator
    that is provided in the string is used in the returned value. Input date
    should be in the format YYYY-MM-DD hh:mm...
    
    Args:
        date (str): Date to be processed.
        
    Returns:
        Date in the format DD/MM/YYYY.
    """
    separator = '/'
    date_part = date[:10]
    day = date_part[8:10]
    month = date_part[5:7]
    year = date_part[0:4]
    return day + separator + month + separator + year


def extract_students(students, data_pos):
    """Return students with 'FitNZ' in the custom field.
    
    Args:
        students (list): Student data.
        data_pos (int): Position of data column to be checked.
    
    Returns:
        updated_students (list): List of students with 'FitNZ'.
    """
    updated_students = []
    for student in students:
        if 'FitNZ' in student[data_pos]:
            updated_students.append(student)
    return updated_students


def extract_student_id(student, data_pos):
    """Return the student's Student ID.
    
    Finds the Student ID by searching in the string for 'FitNZ' and then taking
    those characters plus the next four.
    
    Args:
        student (list): Individual student data.
        data_pos (int): Position of data column to be processed.
    
    Returns:
        student_id (str): Extracted Student ID number.
    """
    start = student[data_pos].find('FitNZ')
    finish = start + 9
    return student[data_pos][start:finish]


def generate_time_string():
    """Generate a timestamp for file names.

    Returns:
        time_str (str): String of timestamp in the format yymmdd-hhmmss.
    """
    time_str = time.strftime('%y%m%d-%H%M%S')
    return time_str


def get_courses(students, course_pos):
    """Return students with a course code in format (XXX-XX-XXX).
    
    Args:
        students (list): Student data.
        course_pos (int): Position in student data of the Course data.
        
    Returns:
        updated_students (list): Students with a course code in correct format.
    """
    updated_students = []
    for student in students:
        if extract_course_code(student[course_pos]) != 'Skip':
            updated_students.append(student)
    return updated_students


def load_data(file_name, source):
    """Read data from a file.

    Args:
        file_name (str): The name of the file to be read.
        source (str): The code for the table that the source data belongs to.

    Returns:
        read_data (list): A list containing the data read from the file.
        True if warnings list has had items appended to it, False otherwise.
        warnings (list): Warnings that have been identified in the data.
    """
    read_data = []
    warnings = []
    # print('File name = ' + str(file_name))
    # Check that file exists
    valid_file = False
    while valid_file is False:
        try:
            file = open(file_name + '.csv', 'r')
        except IOError:
            print('The file does not exist. Check file name.')
            file_name = input('What is the name of the file? ')
        else:
            file.readline()
            reader = csv.reader(file, delimiter=',', quotechar='"')
            for row in reader:
                if row[0] not in (None, ''):
                    read_data.append(row)
            file.close()
            # Check that data has entries for each required column
            if source == 'ed':
                check_ed(read_data)
            valid_file = True
    if len(warnings) > 0:
        return read_data, True, warnings
    else:
        return read_data, False, warnings


def main():
    repeat = True
    while repeat is True:
        try_again = False
        main_message()
        try:
            action = int(input('\nPlease enter the number for your '
                               'selection --> '))
        except ValueError:
            print('Please enter a number between 1 and 2.')
            try_again = True
        else:
            if int(action) < 1 or int(action) > 2:
                print('\nPlease select from the available options (1 - 2)')
                try_again = True
            elif action == 1:
                process_enrolment_dates()
            elif action == 2:
                print('\nIf you have generated any files, please find them '
                      'saved to disk. Goodbye.')
                sys.exit()
        if not try_again:
            repeat = check_repeat()
    print('\nPlease find your files saved to disk. Goodbye.')


def main_message():
    """Print the menu of options."""
    print('\n\n*************==========================*****************')
    print('\nEnrolments Dates Field Checker version 1.0')
    print('Created by Jeff Mitchell, 2018')
    print('\nOptions:')
    print('\n1 Check Dates Fields')
    print('2 Exit')


def process_enrolment_dates():
    """Return lists of students with incorrect dates in their profile fields.
    
    Finds students with incorrect start or end dates when compared to the
    enrolment dates for the course within the Learning Platform.
    
    Returns:
        Students with incorrect Start Date.
        Students with incorrect End Date.
        Students that have both dates incorrect.
    """
    warnings = ['\nProcessing Enrolment Dates Warnings:\n']
    warnings_to_process = False
    print('\nEnrolment Dates data.')
    # Confirm the required files are in place
    required_files = ['Enrolments (Learning Platform)', 'Custom Fields']
    confirm_files('Enrolment Dates Report', required_files)
    # Load file Enrolment Dates
    ed_file_name = input('\nWhat is the name of the Enrolment Dates '
                         'file? --> ')
    raw_ed_data, to_add, warnings_to_add = load_data(ed_file_name, 'ed')
    # Extract Enrolment Dates data:
    # Remove non (XXX-XXX-XXX) courses
    ed_data = get_courses(raw_ed_data, 2)
    # debug_list(ed_data)
    # Clean Start Date into DD/MM/YYYY
    ed_data = clean_date(ed_data, 3)
    ed_data = clean_date(ed_data, 4)
    # debug_list(ed_data)    
    # Load file Custom Fields
    cf_file_name = input('\nWhat is the name of the Custom Fields file? --> ')
    raw_cf_data, to_add, warnings_to_add = load_data(cf_file_name, 'cf')
    # debug_list(raw_cf_data)
    # Extract custom fields data:
    # Remove items without a Student ID (Find 'FitNZ' and add to list)
    cf_data = extract_students(raw_cf_data, 3)
    # debug_list(cf_data)
    # Add Student ID to data for each student
    cf_data = add_student_id(cf_data, 3)
    # debug_list(cf_data)
    # Find 'Course Start Date' and extract date
    cf_data = add_start_date(cf_data, 3)
    # Find 'Course End Date' and extract date
    cf_data = add_end_date(cf_data, 3)
    # debug_list(cf_data)
    # Store in a list
    cf_data = strip_cf_data(cf_data)
    # debug_list(cf_data)
    # Compare lists to find Start Date and End Date errors
    start_change = compare(ed_data, cf_data, 3, 1)
    # debug_list(start_change)
    end_change = compare(ed_data, cf_data, 4, 2)
    # debug_list(end_change)
    # Save lists to csv files
    headings = ('Student ID,Start Date')
    save_data_upload(start_change, headings, 'Start_Changes_')
    headings = ('Student ID,End Date')
    save_data_upload(end_change, headings, 'End_Changes_')
    process_warning_log(warnings, warnings_to_process)


def process_error_log(errors, source):
    """Process an Error log.

    Prints a list of fatal errors in the source data. Saves the errors to file
    and then exits the program.

    Args:
        errors (list): List of errors found in the source data.
        source (str): The name of the source data.
    """
    print('\nThe following errors have been identified in the ' + source
          + ' data: \n')
    for line in errors:
        print(line)
    current_time = generate_time_string()
    error_file = 'Error_log_' + '_' + current_time + '.txt'
    print('\nThe errors have been saved to the error log file.\n')
    save_error_log(source, errors, error_file)
    print('The program will now close. Please correct errors before'
          ' trying again.')
    input('Press enter key to exit. ')
    raise SystemExit


def process_warning_log(warnings, required):
    """Process a Warnings log.

    If required, prints a list of non-fatal errors in the source data. Saves
    the errors to file. If it is not required (e.g. there has not been any data
    appended to the warnings list) then the function returns without any
    action.

    Args:
        warnings (list): List of errors or potential issues found in the source
        data.
        required (str): If True the function will run, if False then it is
        skipped.
    """
    if not required:
        return
    print('\nThere were errors found in one or more of the data sources. '
          'You should check these errors and correct if necessary before '
          'using the generated files. If you correct the files, it is '
          'recommended that you run this program again to generate new '
          'output files from the correct data.')
    review = check_review_warnings()
    if review:
        for line in warnings:
            print(line)
    current_time = generate_time_string()
    warning_file = 'Warning_log_' + '_' + current_time + '.txt'
    print('\nThe warnings have been saved to the warning log file.\n')
    save_warning_log(warnings, warning_file)


def save_data_upload(i_data, headings, d_name):
    """Saves to text file data to be used for uploading to database.

     Args:
        i_data (list): Data that is to be written to file.
        headings (str): Headings to be written to the file.
        d_name (str): Name of the file to be saved.
    """
    # print(i_data)
    time_now = generate_time_string()
    f_name = d_name + time_now + '.txt'
    file_available = False
    while file_available is not True:
        try:
            open(f_name, 'w')
        except IOError:
            print('The file is not accessible. Try a different file name.')
            f_name = input('\nWhat file would you like to save to? --> ')
            + '.txt'
        else:
            f = open(f_name, "w")
            f.write(headings + '\n')
            save_data = ''
            for item in i_data:
                line = ''
                for element in item:
                    line = line + element + ','
                # Remove final comma
                line_to_save = line[:-1]
                save_data = save_data + str(line_to_save) + '\n'
            f.write(save_data)
            file_available = True
        f.close()
    print(d_name + ' has been saved to ' + f_name)


def save_error_log(source, error_log, file_name):
    """Save to file the error log.

    Args:
        source (str): Name of the source file or data.
        error_log (list): The errors to be written.
        file_name (str): Name to save the file to.
    """
    try:
        open(file_name, 'w')
    except IOError:
        print('Error log could not be saved as it is not accessible.')
    else:
        FO = open(file_name, 'w')
        FO.write(str(source) + '\n')
        for line in error_log:
            FO.write(str(line) + '\n')
        FO.close()
        print('Error log has been saved to ' + str(file_name))


def save_warning_log(warning_log, file_name):
    """Save to file the warnings log.

    Args:
        warning_log (list): The errors to be written.
        file_name (str): Name to save the file to.
    """
    try:
        open(file_name, 'w')
    except IOError:
        print('Warning log could not be saved as it is not accessible.')
    else:
        FO = open(file_name, 'w')
        for line in warning_log:
            FO.write(str(line) + '\n')
        FO.close()
        print('Warnings log has been saved to ' + str(file_name))


def strip_cf_data(data):
    """Remove unwanted columns from cf_data.
    
    Returns the following columns: StudentID, Course Start Date, Course End
    Date.
    
    Args:
        data (list): cf_data.
        
    Returns:
        updated_data (list): cf_data with columns removed.
    """
    updated_data = []
    for student in data:
        updated_student = []
        updated_student.append(student[5])
        updated_student.append(student[6])
        updated_student.append(student[7])
        updated_data.append(updated_student)
    return updated_data


if __name__ == '__main__':
    main()