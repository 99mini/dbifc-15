import path from "path";
import fs from "fs";

const outputDir = path.join("logs");

const methodMap = {
  log: "LOG",
  info: "INF",
  warn: "WRN",
  error: "ERR",
};

class Logger {
  /**@type {null | Logger } */
  _instance = null;

  /**@type {string[]} */
  logs = [];

  /**@type {string} */
  filename = "";

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

  _insertLog(message) {
    fs.appendFileSync(this.filename, message + "\n", "utf-8");
  }

  /**
   *
   * @param {string} message
   * @param {{log|info|warn|error}} method
   * @param {boolean} dev
   *
   */
  _log(message, method = "log", dev = false) {
    const timestamp = new Date().toISOString();
    const logMessage = `${methodMap[method]}\t[${timestamp}]\t"${message}"`;
    this.logs.push(logMessage);

    if (dev) {
      console[method](logMessage);
    }

    this._insertLog(logMessage);
  }

  init() {
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    this.filename = path.join(outputDir, `log_${new Date().toISOString()}.log`);

    fs.writeFileSync(this.filename, "", "utf-8");

    this.info("Logger initialized");
  }

  log(message, dev = false) {
    this._log(message, "log", dev);
  }

  error(message, dev = false) {
    this._log(message, "error", dev);
  }

  info(message, dev = false) {
    this._log(message, "info", dev);
  }

  warn(message, dev = false) {
    this._log(message, "warn", dev);
  }

  /**
   * @description progress log (dev only, not saved to log file). normalized to 25 chars
   * @param {number} total
   * @param {number} current
   * @param {string} msg
   * @example
   * logger.progress(100, 0); // $ [__________] 0/100
   * logger.progress(100, 50); // $ [##################] 50/100
   * logger.progress(100, 100, "Finished"); // $ [##################] 100/100 (Finished)
   */
  progress(total, current, msg = "") {
    const progress = Math.floor((current / total) * 25);
    const progressString = `#${" ".repeat(progress)}${"_".repeat(
      25 - progress
    )}`;
    const message = `[${progressString}] ${current}/${total} ${msg}`;
    this._log(message, "log", true);
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
    this.clear();
  }
}

const logger = new Logger().instance;

export default logger;
