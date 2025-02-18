import path from "path";
import fs from "fs";

/**
 * @example
 * ```js
 * formatWonToNumber("100,000원") // => 100000
 * formatWonToNumber("100,000") // => 100000
 * ```
 */
export function formatWonToNumber(str) {
  const regex = /[\0-9]+원/gi;
  const match = regex.exec(str);
  return match ? parseInt(match[0].replace("원", "").replaceAll(",", "")) : 0;
}

/**
 * @description sleep for ms
 * @param {number} ms
 * @param {Logger?} logger
 * @param {string?} message
 */
export async function sleep(ms, logger, message) {
  if (logger && logger.log) {
    const msg = `💤 Sleeping for ${ms}${message ? `: ${message}` : ""}`;
    logger.log(msg);
  }
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 *
 * @param {number[]} arr
 * @param {number} target
 * @returns
 */
export function binarySearch(arr, target) {
  let left = 0;
  let right = arr.length - 1;

  while (left <= right) {
    const mid = Math.floor((left + right) / 2);
    const midDate = arr[mid];

    if (midDate < target) {
      left = mid + 1;
    } else if (midDate > target) {
      right = mid - 1;
    } else {
      return mid;
    }
  }

  return -1;
}

/**
 *
 * @param {Object[]} jsonData
 * @param {boolean} header
 * @returns
 */
function jsonToCsv(jsonData, header = true) {
  let csv = "";

  const headers = Object.keys(jsonData[0]);
  // Extract headers
  if (header) {
    csv += headers.join(",") + "\n";
  }

  // Extract values
  jsonData.forEach((obj) => {
    const values = headers.map((header) => {
      const val = obj[header];
      if (typeof val === "string" && val.includes(",")) {
        return `"${val}"`;
      }
      return val;
    });
    csv += values.join(",") + "\n";
  });

  return csv;
}

/**
 *
 * @param {Object} data
 * @param {string} title
 */
export function saveData(jsonDataWithHeader, title) {
  const csv = jsonToCsv(jsonDataWithHeader);
  const outputDir = path.join("output");
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const filename = path.join(outputDir, `${title}.csv`);
  fs.writeFileSync(filename, csv, "utf-8");
}

/**
 *
 * @param {Object[]} jsonData
 * @param {string} title
 */
export function appendData(jsonData, title) {
  let header = true;
  if (fs.existsSync(path.join("output", `${title}.csv`))) {
    header = false;
  }
  const csv = jsonToCsv(jsonData, header);

  const outputDir = path.join("output");

  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const filename = path.join(outputDir, `${title}.csv`);
  fs.appendFileSync(filename, csv, "utf-8");
}

export function clearOutput() {
  const outputDir = path.join("output");
  if (fs.existsSync(outputDir)) {
    fs.rmSync(outputDir, { recursive: true });
  }
}

/**
 *
 * @param {ProductMetaData} data
 */
export function appendMetaInfo(data, target = "product_meta_data.csv") {
  const filename = path.join("output", target);

  if (!fs.existsSync(filename)) {
    const header = Object.keys(data).join(",");

    fs.mkdirSync("output", { recursive: true });

    fs.writeFileSync(filename, header + "\n", "utf-8");
  }

  const csvRow = Object.values(data).join(",");

  fs.appendFileSync(filename, csvRow + "\n", "utf-8");
}

/**
 *
 * @param {string} name file name wihout extension
 * @returns
 */
export function readLastLine(name) {
  try {
    const data = fs.readFileSync(path.join("output", name), "utf-8");
    const lines = data.split("\n");
    return lines[lines.length - 2];
  } catch (error) {
    return null;
  }
}

export function getLineCount(name) {
  try {
    const data = fs.readFileSync(path.join("output", name), "utf-8");
    const lines = data.split("\n");
    return lines.length - 1;
  } catch (error) {
    return 0;
  }
}

/**
 *
 * @param {string} csv
 * @param {string[]} header ["name", "age"]
 * @param {boolean?} multiLine
 * @returns
 */
export function csvToJson(csv, header, multiLine = false) {
  const lines = multiLine ? csv.split("\n") : [csv];
  const headers = header ? header : lines[0].split(",");

  const result = [];
  for (let i = multiLine ? 1 : 0; i < lines.length; i++) {
    const obj = {};
    const currentLine = lines[i].split(",");
    for (let j = 0; j < headers.length; j++) {
      obj[headers[j]] = currentLine[j];
    }
    result.push(obj);
  }
  return result;
}

/**
 *
 * @param {string} csv
 * @returns
 */
export function hasDuplicatesFromCsv(csv) {
  const lines = csv.split("\n");
  const uniqueLines = new Set(lines);
  return lines.length !== uniqueLines.size;
}

/**
 *
 * @param {string} csv
 * @returns
 */
export function removeDuplicatesFromCsv(csv) {
  const lines = csv.split("\n");
  const header = lines[0];
  const uniqueLines = new Set(lines.slice(1));
  return [header, ...uniqueLines].join("\n");
}

/**
 *
 * @param {*} csv
 * @param {*} title file name with extension
 */
export function saveCSV(csv, title) {
  const outputDir = path.join("output");
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const filename = path.join(outputDir, title);

  if (fs.existsSync(filename)) {
    fs.rmSync(filename);
  }

  fs.writeFileSync(filename, csv, "utf-8");
}

export function getAllOutputFiles() {
  return fs.readdirSync("output");
}

/**
 *
 * @param {string} name file name with extension
 * @returns
 */
export function readCsv(name) {
  return fs.readFileSync(path.join("output", name), "utf-8");
}

/**
 * @description Remove duplicates from all output files
 * @returns {number} count of files with duplicates removed
 */
export function removeDuplicatesAndOverWrite() {
  const files = getAllOutputFiles();

  let count = 0;

  for (const file of files) {
    const csv = readCsv(file);
    if (hasDuplicatesFromCsv(csv)) {
      const uniqueCsv = removeDuplicatesFromCsv(csv);
      count++;
      saveCSV(uniqueCsv, file);
    }
  }

  return count;
}

export function dropZeroRows(target) {
  const csv = readCsv(target);
  const lines = csv.split("\n");

  const nonZeroLines = lines.filter((line) => {
    const values = line.split(",").map((val) => val.trim());
    return !values.some((val) => val === "0");
  });

  const csvWithoutZero = nonZeroLines.join("\n");
  saveCSV(csvWithoutZero, target);
}

export function findFileById(id) {
  const files = getAllOutputFiles();
  return files.find((file) => file.startsWith(id));
}

/**
 * @description Find non-scraped product by meta data
 * @param {string} metaFileName "product_meta_data.csv | product_meta_data2.csv"
 * @returns {{string[]}}스크레핑되지 않은 상품 id 리스트
 */
export function findNonScrapedProductByMetaData(metaFileName) {
  const metaFile = readCsv(metaFileName);
  const files = getAllOutputFiles();
  const meta = csvToJson(
    metaFile,
    ["product_id", "name", "original_price", "brand"],
    true
  );

  const ids = meta.map((item) => item.product_id);
  const fileIds = files.map((file) => file.split(".")[0]);

  const ret = ids.filter((id) => !fileIds.includes(id));

  return ret;
}
