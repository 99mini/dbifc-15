import scraper from "./scraper.js";
import { removeDuplicatesAndOverWrite, dropZeroRows } from "./utils.js";

async function main() {
  // await scraper.run();
  // await scraper.test();
  removeDuplicatesAndOverWrite();
  dropZeroRows("product_meta_data2.csv");
}

main();
