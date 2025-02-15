import scraper from "./scraper.js";
import { removeDuplicatesAndOverWrite } from "./utils.js";

async function main() {
  await scraper.run();
  // await scraper.test();
  removeDuplicatesAndOverWrite();
}

main();
