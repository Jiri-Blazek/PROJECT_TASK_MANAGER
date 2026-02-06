const program = document.body.dataset.program;

const INPUT_FILE_LIST = {
    word: ['C:\\Dokumenty', 'C:\\Dokumenty\\Cars\\'],
    excel: ['C:\\Dokumenty', 'C:\\Excel\\'],
    powerpoint: ['C:\\Dokumenty', 'C:\\Slides\\']
};

// ================== ELEMENTS ==================

const selectWorkDir = document.getElementById("selectWorkDir");
const submitButton = document.getElementById("submitTask");
const inputList = document.querySelectorAll(".submit_value");
const numberInputs = document.querySelectorAll(".number");

const submitInfo = document.getElementById("submitInfo");
const submitInfoContent = document.getElementById("submitInfoContent");
const closeButton = document.getElementById("closeButton");

// ================== INIT ==================

let workDir = null;

INPUT_FILE_LIST[program].forEach((el, index) => {
    const option = document.createElement("option");
    option.textContent = el;
    selectWorkDir.appendChild(option);
    if (index === 0) workDir = el;
});

selectWorkDir.addEventListener("change", e => {
    workDir = selectWorkDir.value;
});

// ================== SUBMIT ==================

submitButton.addEventListener("click", e => {
    const values = collectValues();
    const message = checkValues();
    showSubmitInfo(message);
});

// ================== FUNCTIONS ==================

function collectValues() {
    const data = { program, workDir };

    inputList.forEach(item => {
        data[item.id] = item.value;
    });

    console.log("SUBMIT DATA:", data);
    return data;
}

function checkValues() {
    const errors = [];

    numberInputs.forEach(item => {
        if (item.value === "" || isNaN(Number(item.value))) {
            errors.push(item.id);
        }
    });

    if (errors.length) {
        return ["Error, following inputs must be numbers:", ...errors];
    }

    return ["Task was submitted."];
}

function showSubmitInfo(text) {
    submitInfo.classList.remove("is-hidden");

    text.forEach(line => {
        const p = document.createElement("p");
        p.textContent = line;
        submitInfoContent.appendChild(p);
    });
}

closeButton.addEventListener("click", () => {
    submitInfo.classList.add("is-hidden");
    submitInfoContent.innerHTML = "";
});