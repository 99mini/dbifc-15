import scraper from "./scraper.js";
import {
  removeDuplicatesAndOverWrite,
  findNonScrapedProductByDate,
  findNonScrapedProductByMetaData,
} from "./utils.js";

const BASE_DATE = "2025-02-01T00:00:00Z";

async function main() {
  await scraper.run();
  // await scraper.test();
  removeDuplicatesAndOverWrite();

  const nonScrapedByMetaData = findNonScrapedProductByMetaData(
    "product_meta_data2.csv"
  );
  console.log("nonScrapedByMetaData", nonScrapedByMetaData);

  const nonScrapedByDate = findNonScrapedProductByDate(BASE_DATE);
  console.log("nonScrapedByDate", nonScrapedByDate);
}

main();
