import scraper from "./scraper.js";
import {
  removeDuplicatesAndOverWrite,
  findNonScrapedProductByDate,
  findNonScrapedProductByMetaData,
  getTradingVolumeForAllProducts,
} from "./utils.js";

import { spawn } from "node:child_process";

// FIXME: 기준일을 늘렸을 경우 거래량이 너무 많아서 과거의 데이터를 취하지 못한 데이터를 반영하지 못함

const BASE_DATE = "2025-01-15T00:00:00Z";
const END_DATE = "2025-02-15T00:00:00Z";

async function main() {
  // await scraper.run();
  // await scraper.test();
  removeDuplicatesAndOverWrite();

  const nonScrapedByMetaData = findNonScrapedProductByMetaData(
    "product_meta_data2.csv"
  );
  console.log("nonScrapedByMetaData", nonScrapedByMetaData);

  const nonScrapedByDate = findNonScrapedProductByDate(BASE_DATE);
  console.log("nonScrapedByDate", nonScrapedByDate, nonScrapedByDate.length);

  const tradingVolume = getTradingVolumeForAllProducts(BASE_DATE, END_DATE)
    .sort((a, b) => b.volume - a.volume)
    .slice(0, 100);

  console.log("tradingVolume", tradingVolume);

  const validDateList = [];
  let count = 0;
  for (const tradingVolumeData of tradingVolume) {
    if (nonScrapedByDate.includes(tradingVolumeData.product_id.toString())) {
      console.log(
        `기준일까지 데이터가 존재하지 않습니다. ${tradingVolumeData.product_id}`
      );
      count++;
    } else {
      validDateList.push(tradingVolumeData);
    }
  }

  console.log("기준일까지 데이터가 존재하지 않는 거래량 상위 종목 수: ", count);

  console.log(
    `기준일까지 데이터가 존재하는 거래량 상위 종목 리스트: ${validDateList.length} 개`,
    validDateList
  );

  spawn(`rm ../source/trading/*.csv`, { shell: true });

  for (const validData of validDateList) {
    spawn(`cp output/${validData.product_id}.csv ../source/trading`, {
      shell: true,
    });
  }

  process.exit();
}

main();
