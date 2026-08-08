/**
 * ============================================================
 * VGU DRIVE INVENTORY SYSTEM
 * PART-1 : CORE SCANNER
 * ============================================================
 */

function scanAllDrives() {

  const ss = SpreadsheetApp.getActiveSpreadsheet();

  const master = ss.getSheetByName("Drive_List");

  if (!master) {

    throw new Error("Drive_List sheet not found.");

  }

  const data = master.getRange(2,1,master.getLastRow()-1,6).getValues();

  data.forEach(function(row){

    const program = row[1];
    const subjectCode = row[2];
    const subjectName = row[3];
    const faculty = row[4];
    const driveLink = row[5];

    if(subjectName=="" || driveLink=="")
  return;

    try{

      const sheetName = subjectName + " | " + faculty;

      scanSingleDrive(
      sheetName,
      driveLink
      );

    }

    catch(err){

      Logger.log(subjectName + " : " + err);

    }

  });

}




function scanSingleDrive(courseName,driveLink){

  const ss=SpreadsheetApp.getActiveSpreadsheet();

  const folderId=getGoogleDriveId(driveLink);

  const root=DriveApp.getFolderById(folderId);

  let sheet=ss.getSheetByName(courseName);

  if(sheet==null){

    sheet=ss.insertSheet(courseName);

  }

  else{

    sheet.clearContents();

  }

  sheet.appendRow([
    "S.No",
    "Level",
    "Folder Path",
    "Item Name",
    "Type",
    "Extension",
    "Size KB",
    "Last Updated",
    "URL"
  ]);

  let serial=1;

  function scan(folder,path,level){

      sheet.appendRow([
        serial++,
        level,
        path,
        folder.getName(),
        "Folder",
        "",
        "",
        "",
        folder.getUrl()
      ]);

      const files=folder.getFiles();

      while(files.hasNext()){

        const file=files.next();

        const name=file.getName();

        const ext=name.indexOf(".")>-1
                  ?name.split(".").pop()
                  :"";

        sheet.appendRow([
          serial++,
          level+1,
          path,
          name,
          "File",
          ext,
          Math.round(file.getSize()/1024),
          file.getLastUpdated(),
          file.getUrl()
        ]);

      }

      const folders=folder.getFolders();

      while(folders.hasNext()){

        const sub=folders.next();

        scan(
          sub,
          path+"/"+sub.getName(),
          level+1
        );

      }

  }

  scan(root,root.getName(),0);

}




function getGoogleDriveId(link){

  const patterns=[

    /\/folders\/([a-zA-Z0-9_-]+)/,

    /\/d\/([a-zA-Z0-9_-]+)/,

    /[?&]id=([a-zA-Z0-9_-]+)/

  ];

  for(let p of patterns){

    const m=link.match(p);

    if(m){

      return m[1];

    }

  }

  throw new Error("Invalid Drive Link");

}
function generateDashboard() {

  const ss = SpreadsheetApp.getActiveSpreadsheet();

  const dashboard = ss.getSheetByName("Dashboard");

  dashboard.clear();

  dashboard.appendRow([
    "Program",
    "Subject Code",
    "Subject",
    "Faculty",
    "Total Files",
    "Modules",
    "Handout",
    "TLP",
    "Lab Manual",
    "Assignments",
    "Last Updated",
    "Missing",
    "Status"
  ]);

  const driveMap = loadDriveListMap();

  const ignoreSheets = [
    "Drive_List",
    "Rules",
    "Dashboard"
  ];

  const sheets = ss.getSheets();

  for (let s of sheets) {

    if (ignoreSheets.includes(s.getName()))
      continue;

    analyzeSheet(
      s,
      dashboard,
      driveMap
    );

  }

}
function analyzeSheet(sheet, dashboard, driveMap) {

  const data = sheet.getDataRange().getValues();

  let totalFiles = 0;
  let lastUpdated = null;

  let handout = false;
  let tlp = false;
  let lab = false;

  let assignments = 0;

  const modules = new Set();

  for (let i = 1; i < data.length; i++) {

    const name = String(data[i][3]).toLowerCase();
    const type = String(data[i][4]);

    if (type != "File")
      continue;

    totalFiles++;

    //-----------------------
    // Last Updated
    //-----------------------

    const updated = data[i][7];

    if (updated) {

      if (lastUpdated == null || updated > lastUpdated) {

        lastUpdated = updated;

      }

    }

    //-----------------------
    // Handout
    //-----------------------

    if (
      name.includes("handout") ||
      name.includes("course handout") ||
      name.includes("course handbook")
    ) {

      handout = true;

    }

    //-----------------------
    // TLP
    //-----------------------

    if (
      name.includes("tlp") ||
      name.includes("teaching learning plan") ||
      name.includes("teaching lecture plan")
    ) {

      tlp = true;

    }

    //-----------------------
    // Lab Manual
    //-----------------------

    if (
      name.includes("lab manual") ||
      name.includes("laboratory manual") ||
      name.includes("lab mannual")
    ) {

      lab = true;

    }

    //-----------------------
    // Assignment
    //-----------------------

    if (name.includes("assignment")) {

      assignments++;

    }

    //-----------------------
    // Modules
    //-----------------------

    detectModules(name, modules);

  }

  //-----------------------
  // Missing
  //-----------------------

  const missing = [];

  if (!handout)
    missing.push("Handout");

  if (!tlp)
    missing.push("TLP");

  if (!lab)
    missing.push("Lab Manual");

  for (let i = 1; i <= 5; i++) {

    if (!modules.has(i)) {

      missing.push("Module " + i);

    }

  }

  //-----------------------
  // Status
  //-----------------------

  let status = "🟢 Complete";

  if (missing.length > 0)
    status = "🟡 Pending";

  //-----------------------
  // Metadata
  //-----------------------

  const meta = driveMap[sheet.getName()];

  dashboard.appendRow([

    meta ? meta.program : "",

    meta ? meta.subjectCode : "",

    meta ? meta.subject : sheet.getName(),

    meta ? meta.faculty : "",

    totalFiles,

    modules.size + "/5",

    handout ? "✅" : "❌",

    tlp ? "✅" : "❌",

    lab ? "✅" : "❌",

    assignments,

    lastUpdated,

    missing.join(", "),

    status

  ]);

}
function detectModules(name, modules) {

  const patterns = {

    1: [
      "module 1",
      "module-1",
      "module_1",
      "unit 1",
      "unit-1",
      "unit_1",
      "unit i",
      "unit-i"
    ],

    2: [
      "module 2",
      "module-2",
      "module_2",
      "unit 2",
      "unit-2",
      "unit_2",
      "unit ii",
      "unit-ii"
    ],

    3: [
      "module 3",
      "module-3",
      "module_3",
      "unit 3",
      "unit-3",
      "unit_3",
      "unit iii",
      "unit-iii"
    ],

    4: [
      "module 4",
      "module-4",
      "module_4",
      "unit 4",
      "unit-4",
      "unit_4",
      "unit iv",
      "unit-iv"
    ],

    5: [
      "module 5",
      "module-5",
      "module_5",
      "unit 5",
      "unit-5",
      "unit_5",
      "unit v",
      "unit-v"
    ]

  };

  for (let m in patterns) {

    for (let p of patterns[m]) {

      if (name.includes(p)) {

        modules.add(Number(m));

      }

    }

  }

}
function loadRules() {

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName("Rules");

  if (!sheet) {
    throw new Error("Rules sheet not found.");
  }

  const data = sheet.getDataRange().getValues();

  const rules = {};

  for (let i = 1; i < data.length; i++) {

    const category = String(data[i][0]).trim();

    const keyword = String(data[i][1]).trim().toLowerCase();

    const searchIn = String(data[i][2]).trim();

    if (!category || !keyword)
      continue;

    if (!rules[category]) {

      rules[category] = [];

    }

    rules[category].push({

      keyword: keyword,

      searchIn: searchIn

    });

  }

  return rules;

}
function testRules() {

  const rules = loadRules();

  Logger.log(JSON.stringify(rules,null,2));

}
function matchCategory(name, type, rules) {

  name = String(name).toLowerCase();
  type = String(type);

  for (const category in rules) {

    const keywords = rules[category];

    for (const item of keywords) {

      if (
        item.searchIn != "Both" &&
        item.searchIn != type
      ) {
        continue;
      }

      if (name.includes(item.keyword)) {

        return category;

      }

    }

  }

  return null;

}
function testMatchCategory() {

  const rules = loadRules();

  Logger.log(matchCategory(
    "Course Handout DBMS.pdf",
    "File",
    rules
  ));

  Logger.log(matchCategory(
    "TLP_DBMS.docx",
    "File",
    rules
  ));

  Logger.log(matchCategory(
    "Notes",
    "Folder",
    rules
  ));

  Logger.log(matchCategory(
    "Module_3_DBMS.pdf",
    "File",
    rules
  ));

}

function generateDashboardV2() {

  const ss = SpreadsheetApp.getActiveSpreadsheet();

  const dashboard = ss.getSheetByName("Dashboard");

  dashboard.clear();

  dashboard.appendRow([
    "Program",
  "Subject Code",
  "Subject",
  "Faculty",
    "Total Files",
    "Notes",
    "Handout",
    "TLP",
    "Lab Manual",
    "Assignments",
    "Missing",
    "Status"
  ]);

  // Load Rules
  const rules = loadRules();

  // Ignore these sheets
  const ignore = [
    "Drive_List",
    "Rules",
    "Dashboard"
  ];

  const sheets = ss.getSheets();

  for (const sheet of sheets) {

    if (ignore.includes(sheet.getName()))
      continue;

    Logger.log("Scanning : " + sheet.getName());

    analyzeCourseV2(
      sheet,
      dashboard,
      rules
    );

  }

}
function loadDriveListMap() {

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName("Drive_List");

  const data = sheet.getRange(2,1,sheet.getLastRow()-1,6).getValues();

  const map = {};

  data.forEach(function(row){

    const sheetName = row[3] + " | " + row[4];

    map[sheetName] = {

      program : row[1],

      subjectCode : row[2],

      subject : row[3],

      faculty : row[4]

    };

  });

  return map;

}
function checkMissingRepositories() {

  const ss = SpreadsheetApp.getActiveSpreadsheet();

  const driveList = ss.getSheetByName("Drive_List");
  const data = driveList
    .getRange(2, 1, driveList.getLastRow() - 1, 6)
    .getValues();

  const existingSheets = ss.getSheets()
    .map(s => s.getName());

  Logger.log("========== MISSING REPOSITORIES ==========");

  data.forEach(function(row) {

    const program = String(row[1]).trim();
    const subjectCode = String(row[2]).trim();
    const subject = String(row[3]).trim();
    const faculty = String(row[4]).trim();
    const driveLink = String(row[5]).trim();

    const sheetName = subject + " | " + faculty;

    if (!driveLink) {
      Logger.log("NO DRIVE LINK : " + program + " | " + subjectCode + " | " + subject);
      return;
    }

    if (!existingSheets.includes(sheetName)) {
      Logger.log(
        "MISSING SHEET : " +
        program + " | " +
        subjectCode + " | " +
        subject + " | " +
        faculty
      );
    }

  });

}
