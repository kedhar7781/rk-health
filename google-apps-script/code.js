/**
 * RK Health - Google Apps Script Integration
 * Deploy this script as a "Web App" in your Google Apps Script editor.
 * Set Execute as: "Me"
 * Set Who has access: "Anyone"
 */

function doPost(e) {
  try {
    var requestData = JSON.parse(e.postData.contents);
    var action = requestData.action;
    var data = requestData.data;
    
    var response;
    
    switch (action) {
      case "sync_appointment":
        response = syncAppointment(data);
        break;
      case "delete_appointment":
        response = deleteAppointment(data);
        break;
      case "sync_medication":
        response = syncMedication(data);
        break;
      case "delete_medication":
        response = deleteMedication(data);
        break;
      default:
        throw new Error("Invalid action: " + action);
    }
    
    return ContentService.createTextOutput(JSON.stringify(response))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    var errResponse = {
      status: "error",
      message: error.toString()
    };
    return ContentService.createTextOutput(JSON.stringify(errResponse))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// Helper to get or create a sheet tab
function getOrCreateSheet(sheetName, headers) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(sheetName);
  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
    sheet.appendRow(headers);
    // Format headers
    var range = sheet.getRange(1, 1, 1, headers.length);
    range.setFontWeight("bold");
    range.setBackground("#4A90E2");
    range.setFontColor("#FFFFFF");
  }
  return sheet;
}

// 1. Sync Appointment
function syncAppointment(data) {
  var sheet = getOrCreateSheet("Appointments", [
    "Appointment ID", "Patient Name", "Doctor Name", "Date", "Time", "Notes", "Google Event ID", "Last Synced"
  ]);
  
  var apptId = data.id;
  var patientName = data.patient_name;
  var doctorName = data.doctor_name;
  var apptDate = data.appointment_date; // YYYY-MM-DD
  var apptTime = data.appointment_time; // HH:MM
  var notes = data.notes;
  var googleEventId = data.google_event_id;
  
  // Calendar Event Synchronization
  var calendar = CalendarApp.getDefaultCalendar();
  var event;
  
  // Parse date and time to construct a Date object
  var startDateTime = new Date(apptDate + "T" + apptTime + ":00");
  // Set duration to 30 mins by default
  var endDateTime = new Date(startDateTime.getTime() + 30 * 60 * 1000);
  
  var eventTitle = "RK Health: Appointment - " + patientName + " with " + doctorName;
  var eventDescription = "Appointment with " + doctorName + "\nNotes: " + notes + "\nManaged by RK Health Smart Reminder.";
  
  if (googleEventId) {
    try {
      event = calendar.getEventById(googleEventId);
      if (event) {
        event.setTitle(eventTitle);
        event.setTime(startDateTime, endDateTime);
        event.setDescription(eventDescription);
      } else {
        // Event ID existed but event not found, create new
        event = calendar.createEvent(eventTitle, startDateTime, endDateTime, {description: eventDescription});
        googleEventId = event.getId();
      }
    } catch (e) {
      // Catch issues like permission or invalid ID
      event = calendar.createEvent(eventTitle, startDateTime, endDateTime, {description: eventDescription});
      googleEventId = event.getId();
    }
  } else {
    // New event
    event = calendar.createEvent(eventTitle, startDateTime, endDateTime, {description: eventDescription});
    googleEventId = event.getId();
  }
  
  // Search if row already exists in sheet
  var rows = sheet.getDataRange().getValues();
  var rowIdx = -1;
  for (var i = 1; i < rows.length; i++) {
    if (rows[i][0] == apptId) {
      rowIdx = i + 1; // 1-indexed row number
      break;
    }
  }
  
  var timestamp = new Date();
  var rowData = [apptId, patientName, doctorName, apptDate, apptTime, notes, googleEventId, timestamp];
  
  if (rowIdx !== -1) {
    // Update existing row
    sheet.getRange(rowIdx, 1, 1, rowData.length).setValues([rowData]);
  } else {
    // Append new row
    sheet.appendRow(rowData);
  }
  
  return {
    status: "success",
    google_event_id: googleEventId
  };
}

// 2. Delete Appointment
function deleteAppointment(data) {
  var apptId = data.id;
  var googleEventId = data.google_event_id;
  
  // Delete from Calendar
  if (googleEventId) {
    try {
      var calendar = CalendarApp.getDefaultCalendar();
      var event = calendar.getEventById(googleEventId);
      if (event) {
        event.deleteEvent();
      }
    } catch (e) {
      Logger.log("Failed to delete Calendar Event: " + e.toString());
    }
  }
  
  // Delete from Sheet
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Appointments");
  if (sheet) {
    var rows = sheet.getDataRange().getValues();
    for (var i = 1; i < rows.length; i++) {
      if (rows[i][0] == apptId) {
        sheet.deleteRow(i + 1);
        break;
      }
    }
  }
  
  return {
    status: "success",
    message: "Appointment deleted from Sheets and Calendar."
  };
}

// 3. Sync Medication
function syncMedication(data) {
  var sheet = getOrCreateSheet("Medications", [
    "Medication ID", "Medicine Name", "Dosage", "Frequency", "Time", "Status", "Last Synced"
  ]);
  
  var medId = data.id;
  var medName = data.medicine_name;
  var dosage = data.dosage;
  var frequency = data.frequency;
  var reminderTime = data.reminder_time;
  var status = data.status;
  
  var rows = sheet.getDataRange().getValues();
  var rowIdx = -1;
  for (var i = 1; i < rows.length; i++) {
    if (rows[i][0] == medId) {
      rowIdx = i + 1;
      break;
    }
  }
  
  var timestamp = new Date();
  var rowData = [medId, medName, dosage, frequency, reminderTime, status, timestamp];
  
  if (rowIdx !== -1) {
    sheet.getRange(rowIdx, 1, 1, rowData.length).setValues([rowData]);
  } else {
    sheet.appendRow(rowData);
  }
  
  return {
    status: "success",
    message: "Medication synced."
  };
}

// 4. Delete Medication
function deleteMedication(data) {
  var medId = data.id;
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Medications");
  if (sheet) {
    var rows = sheet.getDataRange().getValues();
    for (var i = 1; i < rows.length; i++) {
      if (rows[i][0] == medId) {
        sheet.deleteRow(i + 1);
        break;
      }
    }
  }
  
  return {
    status: "success",
    message: "Medication deleted from Sheets."
  };
}
