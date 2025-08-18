import streamlit as st
import pandas as pd
from datetime import datetime

# Set page config for wider layout
st.set_page_config(page_title="Medical Signout List", layout="wide")

# Initialize session state
if 'patients' not in st.session_state:
    st.session_state.patients = {
        'Unseen': [],
        'Pending transfer': [],
        'Hospitalist - Day admit': '',
        'Hospitalist - Night admit': [],
        'Geriatric overnight - admission': [],
        'Geriatric overnight - consult': [],
        'Geriatric overnight - WCC': [],
        'CMG/CCC': [],
        'Palliative': [],
        'Highland Family Medicine': [],
        'Vent': [],
        'EOU': '',
        'Other': ''
    }

# Initialize none_selected state
if 'none_selected' not in st.session_state:
    st.session_state.none_selected = {
        'Unseen': False,
        'Pending transfer': False,
        'Hospitalist - Night admit': False,
        'Geriatric overnight - admission': False,
        'Geriatric overnight - consult': False,
        'Geriatric overnight - WCC': False,
        'CMG/CCC': False,
        'Palliative': False,
        'Highland Family Medicine': False,
        'Vent': False
    }

# Initialize clear counter for forcing widget refresh
if 'clear_counter' not in st.session_state:
    st.session_state.clear_counter = 0

st.title("Medical Signout List Generator")

# Date input at the top
signout_date = st.date_input(
    "Signout Date:",
    value=datetime.now().date(),
    key="signout_date"
)
st.write("---")

# Define groups with their field requirements
groups_config = {
    'Unseen': {'fields': ['Number', 'Group', 'Name', 'MRN', 'Primary Care', 'Short Summary'], 'done_by': False, 'text_area': False},
    'Pending transfer': {'fields': ['Number', 'Name', 'MRN', 'Short Summary'], 'done_by': False, 'text_area': False},
    'Hospitalist - Day admit': {'text_area': True},
    'Hospitalist - Night admit': {'fields': ['Number', 'Name', 'MRN', 'Primary Care', 'Short Summary', 'Done by'], 'done_by': True, 'text_area': False},
    'Geriatric overnight - admission': {'fields': ['Number', 'Name', 'MRN', 'Primary Care', 'Short Summary', 'Done by'], 'done_by': True, 'text_area': False},
    'Geriatric overnight - consult': {'fields': ['Number', 'Name', 'MRN', 'Primary Care', 'Short Summary'], 'done_by': False, 'text_area': False},
    'Geriatric overnight - WCC': {'fields': ['Number', 'Name', 'MRN', 'Primary Care', 'Short Summary', 'Done by'], 'done_by': True, 'text_area': False},
    'CMG/CCC': {'fields': ['Number', 'Name', 'MRN', 'Primary Care', 'Short Summary', 'Done by'], 'done_by': True, 'text_area': False},
    'Palliative': {'fields': ['Number', 'Name', 'MRN', 'Primary Care', 'Short Summary', 'Done by'], 'done_by': True, 'text_area': False},
    'Highland Family Medicine': {'fields': ['Number', 'Name', 'MRN', 'Primary Care', 'Short Summary', 'Done by'], 'done_by': True, 'text_area': False},
    'Vent': {'fields': ['Number', 'Name', 'MRN', 'Primary Care', 'Short Summary', 'Done by'], 'done_by': True, 'text_area': False},
    'EOU': {'text_area': True},
    'Other': {'text_area': True}
}

# Function to add patient for groups with individual fields
def add_patient_form(group_name, config):
    st.subheader(f"**{group_name}**")
    
    if config.get('text_area', False):
        # Text area for copy-paste groups
        if config.get('has_buttons', False):
            # For groups with buttons - currently none since we removed them
            pass
        else:
            # For text area groups (Hospitalist - Day admit, EOU, Other)
            if group_name == 'Other':
                # Other group - simple text area without Add Numbers button
                current_value = st.session_state.patients.get(group_name, '')
                text_content = st.text_area(
                    f"Paste content for {group_name}:",
                    value=current_value,
                    height=150,
                    key=f"{group_name}_textarea",
                    help="You can paste content and edit text"
                )
                st.session_state.patients[group_name] = text_content
            else:
                # For Hospitalist - Day admit and EOU - with Add Numbers button
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # Safe access to session state
                    current_value = st.session_state.patients.get(group_name, '')
                    text_content = st.text_area(
                        f"Paste content for {group_name}:",
                        value=current_value,
                        height=150,
                        key=f"{group_name}_textarea",
                        help="You can paste content and manually add numbers or edit text"
                    )
                
                with col2:
                    st.write("")  # Add spacing
                    st.write("")  # Add spacing
                    if st.button("Add Numbers", key=f"{group_name}_add_numbers"):
                        # Add numbers to each line
                        lines = text_content.split('\n')
                        numbered_lines = []
                        counter = 1
                        for line in lines:
                            if line.strip():  # Only number non-empty lines
                                numbered_lines.append(f"{counter}. {line}")
                                counter += 1
                            else:
                                numbered_lines.append(line)  # Keep empty lines as is
                        numbered_content = '\n'.join(numbered_lines)
                        st.session_state.patients[group_name] = numbered_content
                        st.rerun()
                
                st.session_state.patients[group_name] = text_content
    else:
        # Individual patient fields
        st.write("")  # Add some spacing
        
        # Ensure the group exists in session state
        if group_name not in st.session_state.patients:
            st.session_state.patients[group_name] = []
        
        # Show existing patients
        patients_to_remove = []
        
        for i, patient in enumerate(st.session_state.patients[group_name]):
            with st.container():
                # Create columns with custom widths - make Summary column wider
                if 'Short Summary' in config['fields']:
                    # Calculate column ratios - give Short Summary more space
                    num_fields = len(config['fields'])
                    col_ratios = []
                    for field in config['fields']:
                        if field == 'Short Summary':
                            col_ratios.append(3)  # 3x wider for summary
                        elif field == 'Number':
                            col_ratios.append(0.5)  # Smaller for number
                        else:
                            col_ratios.append(1)
                    col_ratios.append(0.8)  # Remove button column
                    cols = st.columns(col_ratios)
                else:
                    cols = st.columns(len(config['fields']) + 1)
                
                for j, field in enumerate(config['fields']):
                    if field == 'Done by' and config.get('done_by', False):
                        # Special dropdown for Done by with Other option
                        done_by_options = ['', 'Nocturnist', 'APP', 'resident', 'Other']
                        current_value = patient.get(field, '')
                        
                        # Check if current value is in options
                        if current_value in done_by_options:
                            selected_option = cols[j].selectbox(
                                field,
                                options=done_by_options,
                                index=done_by_options.index(current_value),
                                key=f"{group_name}_{i}_{field}_select"
                            )
                        else:
                            # Current value is custom text, show "Other" as selected
                            selected_option = cols[j].selectbox(
                                field,
                                options=done_by_options,
                                index=done_by_options.index('Other') if current_value else 0,
                                key=f"{group_name}_{i}_{field}_select"
                            )
                        
                        if selected_option == 'Other':
                            # Show text input for custom entry
                            patient[field] = cols[j].text_input(
                                "Custom Done by:",
                                value=current_value if current_value not in done_by_options[:-1] else '',
                                key=f"{group_name}_{i}_{field}_custom"
                            )
                        else:
                            patient[field] = selected_option
                    elif field == 'Group' and group_name == 'Unseen':
                        patient[field] = cols[j].selectbox(
                            field,
                            options=['', 'hospitalist', 'geriatric', 'WCC', 'CMG', 'CCC', 'FMH', 'Palliative', 'Vent'],
                            index=0 if patient.get(field, '') == '' else ['', 'hospitalist', 'geriatric', 'WCC', 'CMG', 'CCC', 'FMH', 'Palliative', 'Vent'].index(patient.get(field, '')),
                            key=f"{group_name}_{i}_{field}"
                        )
                    elif field == 'Primary Care' and group_name == 'Palliative':
                        # Special dropdown for Palliative Primary Care
                        primary_options = ['', 'Nicole Gise', 'Brandon Wilcoxson', 'Edward Shanley', 'Rashmi Khadilkar', 'Chin-Lin Ching', 'Other']
                        current_value = patient.get(field, '')
                        
                        # Check if current value is in options
                        if current_value in primary_options:
                            selected_option = cols[j].selectbox(
                                field,
                                options=primary_options,
                                index=primary_options.index(current_value),
                                key=f"{group_name}_{i}_{field}_select"
                            )
                        else:
                            # Current value is custom text, show "Other" as selected
                            selected_option = cols[j].selectbox(
                                field,
                                options=primary_options,
                                index=primary_options.index('Other') if current_value else 0,
                                key=f"{group_name}_{i}_{field}_select"
                            )
                        
                        if selected_option == 'Other':
                            # Show text input for custom entry
                            patient[field] = cols[j].text_input(
                                "Custom Primary Care:",
                                value=current_value if current_value not in primary_options[:-1] else '',
                                key=f"{group_name}_{i}_{field}_custom"
                            )
                        else:
                            patient[field] = selected_option
                    elif field == 'Primary Care' and group_name == 'Geriatric overnight - admission':
                        # Special dropdown for Geriatric admission Primary Care
                        primary_options = ['', 'Dr. Daniel King', 'Dr. Noel Yarze', 'Dr. Dmitriy Migdalovich', 'Dr. Kevin McCormick', 'Other']
                        current_value = patient.get(field, '')
                        
                        # Check if current value is in options
                        if current_value in primary_options:
                            selected_option = cols[j].selectbox(
                                field,
                                options=primary_options,
                                index=primary_options.index(current_value),
                                key=f"{group_name}_{i}_{field}_select"
                            )
                        else:
                            # Current value is custom text, show "Other" as selected
                            selected_option = cols[j].selectbox(
                                field,
                                options=primary_options,
                                index=primary_options.index('Other') if current_value else 0,
                                key=f"{group_name}_{i}_{field}_select"
                            )
                        
                        if selected_option == 'Other':
                            # Show text input for custom entry
                            patient[field] = cols[j].text_input(
                                "Custom Primary Care:",
                                value=current_value if current_value not in primary_options[:-1] else '',
                                key=f"{group_name}_{i}_{field}_custom"
                            )
                        else:
                            patient[field] = selected_option
                    elif field == 'Short Summary':
                        patient[field] = cols[j].text_area(
                            field,
                            value=patient.get(field, ''),
                            height=80,
                            key=f"{group_name}_{i}_{field}"
                        )
                    else:
                        patient[field] = cols[j].text_input(
                            field,
                            value=patient.get(field, ''),
                            key=f"{group_name}_{i}_{field}"
                        )
                
                # Remove button
                if cols[-1].button("Remove", key=f"{group_name}_remove_{i}"):
                    patients_to_remove.append(i)
        
        # Remove patients marked for removal (immediate effect)
        for i in reversed(patients_to_remove):
            st.session_state.patients[group_name].pop(i)
        
        # If patients were removed, rerun to update the display
        if patients_to_remove:
            st.rerun()
        
        # Show buttons
        col1, col2 = st.columns(2)
        
        # Add patient button
        if col1.button(f"Add Patient", key=f"{group_name}_add_{st.session_state.clear_counter}"):
            # Ensure the group exists before appending
            if group_name not in st.session_state.patients:
                st.session_state.patients[group_name] = []
            st.session_state.patients[group_name].append({})
            if group_name in st.session_state.none_selected:
                st.session_state.none_selected[group_name] = False  # Reset none selection
            st.rerun()
        
        # None button logic
        if len(st.session_state.patients.get(group_name, [])) == 0:
            # Force check: if we just cleared, make sure none_selected is False
            none_selected_status = st.session_state.none_selected.get(group_name, False)
            
            # Show None button with different styles based on selection
            if none_selected_status:
                # None is selected - show with success style
                if col2.button(f"None ✓", key=f"{group_name}_none_{st.session_state.clear_counter}", type="primary"):
                    pass  # Already selected
            else:
                # None is not selected - show normal button
                if col2.button(f"None", key=f"{group_name}_none_{st.session_state.clear_counter}"):
                    if group_name in st.session_state.none_selected:
                        st.session_state.none_selected[group_name] = True
                    st.rerun()
        else:
            # Patients exist, so reset none selection and hide button
            if group_name in st.session_state.none_selected:
                st.session_state.none_selected[group_name] = False
            col2.write("")  # Empty space to maintain layout

# Display all groups
for group_name, config in groups_config.items():
    add_patient_form(group_name, config)
    st.divider()

# Auto-generate report section
st.write("---")
report_container = st.container()

with report_container:
    st.subheader("**SIGNOUT LIST**")
    st.write(f"Date: {signout_date.strftime('%Y-%m-%d')}")
    st.write("---")
    
    # Generate report text for copying
    report_text = f"SIGNOUT LIST\nDate: {signout_date.strftime('%Y-%m-%d')}\n" + "="*50 + "\n\n"
    
    for group_name, config in groups_config.items():
        st.write(f"**{group_name.upper()}**")
        report_text += f"{group_name.upper()}\n"
        
        if config.get('text_area', False):
            # For text area groups
            if config.get('has_buttons', False):
                # Special handling for groups with buttons (currently none)
                pass
            else:
                # Regular text area groups (Hospitalist - Day admit, EOU, Other)
                content = st.session_state.patients[group_name].strip()
                if content:
                    # Display with preserved line breaks
                    for line in content.split('\n'):
                        if line.strip():  # Only show non-empty lines
                            st.write(line)
                    report_text += f"{content}\n"
                else:
                    st.write("None")
                    report_text += "None\n"
        else:
            # For individual patient groups
            patients = st.session_state.patients[group_name]
            has_patients = False
            
            for patient in patients:
                # Check if patient has any data
                if any(patient.get(field, '').strip() for field in config['fields']):
                    has_patients = True
                    patient_info = []
                    for field in config['fields']:
                        value = patient.get(field, '').strip()
                        if value:
                            if field == 'Number':
                                patient_info.append(f"{value}.")
                            else:
                                patient_info.append(f"{field}: {value}")
                    
                    if patient_info:
                        patient_line = " | ".join(patient_info)
                        st.write(patient_line)
                        report_text += f"{patient_line}\n"
            
            if not has_patients:
                st.write("None")
                report_text += "None\n"
        
        st.write("")
        report_text += "\n"

# Copy to clipboard section
st.write("---")
st.subheader("📋 Copy Report")

# Display the formatted text in a text area for easy copying
st.text_area(
    "Select all text below and copy (Ctrl+A, Ctrl+C):",
    value=report_text,
    height=200,
    key="copy_text_area"
)