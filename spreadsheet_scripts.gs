// @JaredKreppein
// 09/24/2018

// retrieves new emails from gmail inbox every 15 minutes* (Edit -> All your triggers)
// scrape emails from venmo for name and response (completed/declined/paid)
// searches for name in spreadsheet and updates response automatically


// ***** SET-UP *****
// 1) setting up the spreadsheet
//    - can handle any number of rows
//    - columns go as such: [first-name],[last-name],[venmo-payed?]


// * Update every 15 minutes (instead of every minute) to avoid exceeding Google quota
// documentation: https://developers.google.com/apps-script/guides/services/quotas


// color key
// light green    (187, 254, 184):  pitched the alloted amount or more
// light red      (254, 184, 184):  did not pitch
// light yellow   (255, 255, 253):  pitched less than the alloted amount
// clear:                           denied request (not going, don't need to pitch)


// change this to change how pitch/guest calculations are made
PITCH = 5


// MAIN: retrieves emails every cycle and updates spreadsheet accordingly
function main() {
  var venmoMessages = getUnreadEmails();
  for (var i = 0; i < venmoMessages.length; i ++) {
    updateSpreadsheet(venmoMessages[i]);
  }
}


// returns an array of unread emails from venmo
function getUnreadEmails() {
  venmoMessages = [];
  
  // get all unread email threads
  var unreadMessageCount = GmailApp.getInboxUnreadCount();
  Logger.log(unreadMessageCount);
  Logger.log(unreadMessageCount)
  if (unreadMessageCount > 0) {
    var threads = GmailApp.getInboxThreads(0, unreadMessageCount);
    for (var i = 0; i < threads.length; i ++) {
      if (threads[i].isInInbox()) {
        // get all unread email messages
        var messages = threads[i].getMessages();
        for (var j = 0; j < messages.length; j ++) {
          // parse sender's address from email
          var sender = messages[j].getFrom();
          var leftBuffer = sender.indexOf("<");
          var rightBuffer = sender.indexOf(">");
          sender = sender.slice(leftBuffer+1,rightBuffer);
          
          // if message is from venmo - add to array
          if (sender.localeCompare("venmo@venmo.com") == 0) {
            venmoMessages.push(messages[j]);
          }
          // mark as read after being processed
          messages[j].markRead();
        }
      }
    }
  }
  return venmoMessages;
}


// scrapes a single email message and updates spreadsheet
function updateSpreadsheet(message) {
  // get first name, last name, and type (completed, declined, or paid)
  var subject = message.getSubject();
  var subjectArray = subject.split(" ");
  var firstName = subjectArray[0];
  var lastName = subjectArray[1];
  var type = subjectArray[2];
  var amount = subjectArray[4];
  var numericAmount = parseFloat(amount.slice(1));   // convert var amount to float (ex. "$10.67" -> 10.67)
  
  // open spreadsheet
  var sheet = SpreadsheetApp.getActiveSheet();
  var data = sheet.getDataRange().getValues();
  
  for (var i = 0; i < data.length; i ++) {
    // find user in spreadsheet (first and last name match)
    if ( (firstName.localeCompare(data[i][0]) == 0) && (lastName.localeCompare(data[i][1]) == 0) ) {
      // user completed the venmo request
      if (type.localeCompare("completed") == 0) {
        sheet.getRange(i+1, 3).setBackgroundRGB(187, 254, 184);
        sheet.getRange(i+1, 3).setHorizontalAlignment("center");
        sheet.getRange(i+1, 3).setValue(amount);
      }
      // user declined the venmo request
      if (type.localeCompare("declined") == 0) {
        sheet.getRange(i+1, 3).clear();
      }
      // user sent a payment (in case user previously deleted request or pitched for guests)
      if (type.localeCompare("paid") == 0) {
        sheet.getRange(i+1, 3).setHorizontalAlignment("center");
        sheet.getRange(i+1, 3).setValue(sheet.getRange(i+1, 3).getValue() + numericAmount);
        
        if (numericAmount < 5) {
          sheet.getRange(i+1, 3).setBackgroundRGB(255, 255, 153);  // has not met pitch quota
        }
        else {
          sheet.getRange(i+1, 3).setBackgroundRGB(187, 254, 184);
          sheet.getRange(i+1, 4).setHorizontalAlignment("center");
          
          // set number of guests only if pitch is or greater than $10 (pitch for 2 people)
          if (numericAmount >= 10) {
            sheet.getRange(i+1, 4).setValue(Math.floor(numericAmount/5));
          }
        }
      }
    }
  }
}


// resets the spreadsheet (sets all users listed as unpaid and clears guest column)
function resetSpreadsheet() {
  // open spreadsheet
  var sheet = SpreadsheetApp.getActiveSheet();
  var data = sheet.getDataRange().getValues();
  for (var i = 0; i < data.length; i ++) {
    // change everyone's status to unpaid (light red) and remove guests
    if (i != 0) {
      sheet.getRange(i+1, 3).setBackgroundRGB(254, 184, 184);
      sheet.getRange(i+1, 3).setHorizontalAlignment("center");
      sheet.getRange(i+1, 3).setValue(0);
      sheet.getRange(i+1, 4).clear();
    }
  }
}


