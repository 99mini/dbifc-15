import path from "path";
import fs from "fs";

const outputDir = path.join("logs");

class Logger {
  /**@type {null | Logger } */
  _instance = null;

  /**@type {string[]} */
  logs = [];

  /**@type {string} */
  filename = "";

  /**@type {null | number} */
  fd = null;

  constructor() {
    if (Logger._instance) {
      return Logger._instance;
    }
    Logger._instance = this;
  }

  get count() {
    return this.logs.length;
  }

  /** @returns {Logger} */
  get instance() {
    if (!Logger._instance) {
      Logger._instance = new Logger();
    }
    return Logger._instance;
  }

  get allLogs() {
    return this.logs;
  }

  init() {
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    this.filename = path.join(outputDir, `log_${new Date().toISOString()}.log`);

    this.fd = fs.openSync(this.filename, "w");

    fs.writeFileSync(this.filename, "", "utf-8");

    this.info("Logger initialized");
  }

  insertLog() {
    fs.appendFileSync(this.filename, this.logs[this.count - 1] + "\n", "utf-8");
  }

  log(message) {
    const timestamp = new Date().toISOString();
    const logMessage = `LOG\t[${timestamp}]\t"${message}"`;
    this.logs.push(logMessage);
    console.debug(logMessage);

    this.insertLog(logMessage);
  }

  error(message) {
    const timestamp = new Date().toISOString();
    const logMessage = `ERR\t[${timestamp}]\t"${message}"`;
    this.logs.push(logMessage);
    console.error(logMessage);

    this.insertLog(logMessage);
  }

  info(message) {
    const timestamp = new Date().toISOString();
    const logMessage = `INF\t[${timestamp}]\t"${message}"`;
    this.logs.push(logMessage);
    console.info(logMessage);

    this.insertLog(logMessage);
  }

  warn(message) {
    const timestamp = new Date().toISOString();
    const logMessage = `WRN\t[${timestamp}]\t"${message}"`;
    this.logs.push(logMessage);
    console.warn(logMessage);

    this.insertLog(logMessage);
  }

  clear() {
    this.logs = [];
  }

  print() {
    console.log(this.logs.join("\n"));
  }

  save() {
    fs.writeFileSync(this.filename, this.logs.join("\n"), "utf-8");
  }

  close() {
    if (this.fd) {
      fs.closeSync(this.fd);
    }
    this.clear();
  }
}

const logger = new Logger().instance;

export default logger;
