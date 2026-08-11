function analyzeRepository(sheet, rules) {

  const data = sheet.getDataRange().getValues();

  const result = {

    totalFiles: 0,

    handout: false,
    tlp: false,
    labManual: false,

    modules: {
      1: false,
      2: false,
      3: false,
      4: false,
      5: false
    },

    assignments: {
      1: false,
      2: false,
      3: false,
      4: false,
      5: false
    },

    missing: []

  };

  for (let i = 1; i < data.length; i++) {

    const itemName = String(data[i][3]).toLowerCase();

    const type = String(data[i][4]);

    // Count every file anywhere in repository
    if (type == "File") {

      result.totalFiles++;

    }

    // Ignore folders for compliance checking
    if (type != "File")
      continue;

    //-----------------------
    // Category Detection
    //-----------------------

    const category = matchCategory(
      itemName,
      "File",
      rules
    );

    if (category == "Handout")
      result.handout = true;

    if (category == "TLP")
      result.tlp = true;

    if (category == "Lab Manual")
      result.labManual = true;

    //-----------------------
    // Module Detection
    //-----------------------

    detectModules(itemName, result.modules);

    //-----------------------
    // Assignment Detection
    //-----------------------

    detectAssignments(itemName, result.assignments);

  }

  return result;

}
function detectAssignments(name, assignments){

  for(let i=1;i<=5;i++){

    if(
      name.includes("assignment "+i) ||
      name.includes("assignment-"+i) ||
      name.includes("assignment_"+i)
    ){

      assignments[i]=true;

    }

  }

}
function testRepository(){

  const ss = SpreadsheetApp.getActiveSpreadsheet();

  const rules = loadRules();

  const sheet = ss.getSheetByName("Machine Learning");   // kisi bhi course ka naam

  const result = analyzeRepository(sheet,rules);

  Logger.log(JSON.stringify(result,null,2));

}
function detectModules(name, modules) {

  name = name.toLowerCase();

  const patterns = {

    1: ["module 1","module-1","module_1","module1","unit 1","unit-1","unit_1","unit i","unit-i","unit_i"],

    2: ["module 2","module-2","module_2","module2","unit 2","unit-2","unit_2","unit ii","unit-ii","unit_ii"],

    3: ["module 3","module-3","module_3","module3","unit 3","unit-3","unit_3","unit iii","unit-iii","unit_iii"],

    4: ["module 4","module-4","module_4","module4","unit 4","unit-4","unit_4","unit iv","unit-iv","unit_iv"],

    5: ["module 5","module-5","module_5","module5","unit 5","unit-5","unit_5","unit v","unit-v","unit_v"]

  };

  for (const m in patterns) {

    for (const p of patterns[m]) {

      if (name.includes(p)) {

        modules.add(Number(m));

      }

    }

  }

}