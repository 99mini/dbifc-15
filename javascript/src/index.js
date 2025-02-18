import scraper from "./scraper.js";
import { removeDuplicatesAndOverWrite } from "./utils.js";

const BASE_DATE = "2025-02-01T00:00:00Z";

async function main() {
  // await scraper.run();
  // await scraper.test();
  removeDuplicatesAndOverWrite();
}

main();
