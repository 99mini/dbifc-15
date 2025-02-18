/**
 * 총 실행 시간
 * 로그인: 3000 + 5000
 *
 * 한 브랜드 당 크롤링 시간
 *  = 채결 내역 클릭 대기(1000) + 스크롤(SCROLL_DELAY * SCROLL_COUNT)
 *  = 1000 + 1000 * 10
 *  = 11000 (11초)
 *
 * 총 실행 시간
 *  = 로그인(3000 + 5000) + (한 브랜드 당 크롤링 시간 * BRAND_ITEM_LIMIT)
 *  = 3000 + 5000 + (11000 * 10)
 *  = 165000 (165초)
 */

import puppeteer from "puppeteer";
import dotenv from "dotenv";
import { omit } from "es-toolkit";

import {
  sleep,
  saveData,
  formatWonToNumber,
  appendMetaInfo,
  appendData,
  readLastLine,
  csvToJson,
  binarySearch,
  getLineCount,
} from "./utils.js";
import logger from "./logger.js";

dotenv.config();

const ID = process.env.ID;
const PW = process.env.PW;

// MARK: constants
/**
 * 스크롤 1회 => 50개 데이터
 * 10 => 50 * 10 = 500개 데이터
 * */
const SCROLL_COUNT = 20;

/**
 * 이미 수집된 데이터를 제외한 데이터 수집을 위한 offset
 */
let scroll_count_offset = 0;

/**
 * 스크롤 대기 시간 (ms)
 * */
const SCROLL_DELAY = 4000;

/**
 * 브랜드 당 크롤링할 상품 갯수
 */
const BRAND_ITEM_LIMIT = 50;

/**
 * 브랜드 당 크롤링할 상품 시작 offset
 */
const BRAND_ITEM_OFFSET = 0;

/**
 * API 요청 대기 시간 (ms)
 */
const API_CALL_DELAY = 4000;

/** 브랜드 리스트 */
// const BRAND = ["salomon", "reebok", "converse", "asics", ""];
const BRAND = [
  "nike",
  "adidas",
  "jordan",
  "new%20balance",
  "converse",
  "vans",
  "asics",
];
// const BRAND = ["nike"];

/**
 * 브랜드별 크롤링 시작 offset
 */
const BRAND_OFFSET = {
  // nike: 49,
  // adidas: 25,
  // jordan: 30,
  // "new%20balance": 20,
  // converse: 45,
  // vans: 17,
};

/**
 * 브랜드별 크롤링 URL
 * @type {Record<string, string>}
 * @example
 * {
 *   nike: "https://kream.co.kr/brands/Nike?tab=44",
 *   adidas: "https://kream.co.kr/brands/Adidas?tab=44",
 * }
 */
const BRAND_TARGET_MAP = BRAND.reduce((acc, brand) => {
  acc[brand] = `https://kream.co.kr/brands/${brand}?tab=44`;
  return acc;
}, {});

/**
 * @description 응답 초과 대기 flag
 * @type {boolean}
 */
let flag = false;

function getFlag() {
  return flag;
}

/**
 * MARK: Scraper
 * @description scraping data from https://kream.co.kr/
 *
 */
class Scraper {
  /** @type {Record<string, TimeSeriesData[]>} */
  timeSeriesData = {};

  /** @type {ProductMetaData[]} */
  productMetaData = [];

  _instance = null;

  constructor() {
    if (Scraper._instance) {
      return Scraper._instance;
    }
    Scraper._instance = this;
  }

  /**
   * @returns {Scraper}
   */
  get instance() {
    if (!Scraper._instance) {
      Scraper._instance = new Scraper();
    }
    return Scraper._instance;
  }

  report(scrapeTimerList) {
    logger.info(`🎉 크롤링 완료`);
    logger.info(`📦 총 브랜드: ${BRAND.length} 개`);
    logger.info(`📦 총 상품: ${this.productMetaData.length} 개`);
    logger.info(
      `📦 총 데이터: ${Object.values(this.timeSeriesData).flat().length} 건`
    );
    logger.info(`🕒 총 소요 시간: ${new Date().getTime() - startTime}ms`);

    const sortedScrapeTimerList = scrapeTimerList.sort((a, b) => a - b);

    let minTime = scrapeTimerList[0];
    let maxTime = scrapeTimerList[scrapeTimerList.length - 1];
    let medianTime =
      sortedScrapeTimerList[Math.floor(sortedScrapeTimerList.length / 2)];
    let averageTime = 0;

    for (let i = 0; i < scrapeTimerList.length; i++) {
      averageTime += scrapeTimerList[i];
    }

    averageTime /= scrapeTimerList.length;

    logger.info(`🕒 소요 시간 보고서`);
    logger.info(`🕒 최소 소요 시간: ${minTime}ms`);
    logger.info(`🕒 최대 소요 시간: ${maxTime}ms`);
    logger.info(`🕒 평균 소요 시간: ${averageTime}ms`);
    logger.info(`🕒 중앙 소요 시간: ${medianTime}ms`);

    logger.close();
  }

  async run() {
    const startTime = new Date().getTime();
    const scrapeTimerList = [];

    logger.init();

    // clear
    // {
    //   clearOutput();
    // }

    const browser = await puppeteer.launch({
      headless: process.env.NODE_ENV === "production",
    });
    const page = await browser.newPage();

    // Navigate the page to a URL.
    await page.goto("https://kream.co.kr/login");

    logger.info("🚀 크롤링 시작");

    /** @description 네트워크 가로채기 */
    page.on("response", async (response) => {
      try {
        const request = response.request();
        const url = request.url(); // 요청 URL
        const method = request.method(); // 요청 메서드 (GET, POST)

        if (url.includes(`sales`)) {
          // API 요청인지 확인

          const productId = url.split("/sales")[0].split("/").pop();

          // 응답 본문 가로채기
          /** @type {TimeSeriesData[]} */
          const responseBody = await response
            .json()
            .then((res) =>
              res.items.map((item) => omit(item, ["product_option"]))
            );

          if (responseBody && responseBody.length > 0) {
            if (!this.timeSeriesData[productId]) {
              this.timeSeriesData[productId] = [];
            }

            const firstResponseDate = responseBody[0].date_created;

            const lastLine = readLastLine(`${productId}.csv`);

            const lastItem = lastLine
              ? csvToJson(lastLine, [
                  "product_id",
                  "price",
                  "option",
                  "date_created",
                  "is_immediate_delivery_item",
                ])
              : undefined;

            if (
              lastItem &&
              lastItem.length === 1 &&
              new Date(lastItem[0].date_created) < new Date(firstResponseDate)
            ) {
              logger.log(`📌 [${productId}] 이미 수집된 데이터입니다`);

              const dateArr = responseBody.map((item) =>
                new Date(item.date_created).getTime()
              );
              const targetDate = new Date(lastItem[0].date_created).getTime();

              const targetIndex = binarySearch(dateArr, targetDate);

              if (targetIndex !== -1) {
                const slicedRes = responseBody.slice(targetIndex + 1);
                logger.log(
                  `📌 [${productId}] ${slicedRes[0].date_created}부터 저장: ${slicedRes.length}개`
                );

                this.timeSeriesData[productId].push(...slicedRes);
                appendData(slicedRes, productId);
              } else {
                logger.log(`📌 [${productId}] 저장할 데이터가 없습니다`);
              }
            } else {
              logger.log(
                `📌 [${productId}] 새로운 데이터 수집: ${responseBody.length}개`
              );
              this.timeSeriesData[productId].push(...responseBody);

              appendData(responseBody, productId);
            }
          }
        }
      } catch (error) {
        flag = true;

        await sleep(API_CALL_DELAY);

        flag = false;
      }
    });

    // login
    try {
      const loginButton = await page.$("button.btn_login_naver");
      logger.log("🔑 로그인 중");

      if (!loginButton) {
        logger.error("login button not found");
        return;
      }

      await loginButton.click();

      await sleep(3000, logger, "login button click");
    } catch (error) {
      logger.error(`🚫 로그인 실패: ${error}`);
      return;
    }

    // naver login
    try {
      await page.evaluate(
        (id, pw) => {
          document.querySelector("#id").value = id;
          document.querySelector("#pw").value = pw;
        },
        ID,
        PW
      );

      // click login button
      const loginButton = await page.$("button.btn_login");

      await loginButton.click();

      logger.log("🔑 로그인 완료");

      await page.waitForNavigation();
    } catch (error) {
      logger.error(`🚫 로그인 실패: ${error}`);
      return;
    }

    await sleep(5000, logger, "login success");

    // scraping target
    {
      for (const [brand, target] of Object.entries(BRAND_TARGET_MAP)) {
        logger.log(`🔍 브랜드 정보 수집 중: ${brand}`);
        const hrefs = [];

        /** goto target and append hrefs */
        try {
          await page.goto(target);

          await page.waitForSelector(".product_card");

          const products = await page.$$(".product_card > a");

          for (const product of products) {
            const href = await product.evaluate((el) => el.href);

            hrefs.push(href);
          }
        } catch (error) {
          logger.error(`🚫 브랜드 정보 수집 실패: ${error}`);
          continue;
        }

        const offset = BRAND_OFFSET[brand]
          ? BRAND_OFFSET[brand]
          : BRAND_ITEM_OFFSET;
        const hrefsLimited = hrefs.slice(offset, offset + BRAND_ITEM_LIMIT);

        /** scrape details */
        {
          for (
            let hrefCounter = 0;
            hrefCounter < hrefsLimited.length;
            hrefCounter++
          ) {
            // reset offset
            scroll_count_offset = 0;

            const href = hrefsLimited[hrefCounter];

            const productId = href.split("/").pop();

            await page.goto(href);

            await page.waitForSelector(".main-title-container .title");

            const scrapeStartTime = new Date().getTime();

            // scrape meta data
            const name = await page.$eval(
              ".main-title-container .title",
              (el) => el.textContent
            );
            const originalPrice = await page.$eval(
              ".detail-box .product_info",
              (el) => el.textContent
            );

            const newProductMetaData = {
              product_id: productId,
              name,
              original_price: formatWonToNumber(originalPrice),
              brand,
            };

            const lastMetaInfoRaw = readLastLine("product_meta_data2");

            const lastMetaInfo = lastMetaInfoRaw
              ? csvToJson(lastMetaInfoRaw, [
                  "product_id",
                  "name",
                  "original_price",
                  "brand",
                ])
              : undefined;

            if (
              lastMetaInfo &&
              lastMetaInfo.length === 1 &&
              lastMetaInfo[0].product_id === productId
            ) {
              logger.log(
                `📌 [${hrefCounter + 1}/${
                  hrefsLimited.length
                }] 이미 수집된 상품 정보입니다`
              );

              scroll_count_offset = Math.floor(getLineCount(productId) / 50);
            } else {
              logger.log(
                `🔍 [${hrefCounter + 1}/${
                  hrefsLimited.length
                }] 상품 정보 수집 시작: [${brand}]${newProductMetaData.name}(${
                  newProductMetaData.product_id
                })`
              );

              appendMetaInfo(newProductMetaData, "product_meta_data2.csv");
            }

            this.productMetaData.push({
              product_id: productId,
              name,
              original_price: formatWonToNumber(originalPrice),
              brand,
            });

            continue;
            // scrape time series data
            {
              let weightedDelay = API_CALL_DELAY;
              let successScrape = false;

              const retryCount = 5;

              const scrollProductHistory = async (retry) => {
                logger.log(
                  `🔍 [${retry}/${retryCount}] 상품 채결 내역 수집 중: [${brand}]${newProductMetaData.name}(${newProductMetaData.product_id})`
                );
                const timeSeriesBtn = await page.$(
                  "a.btn.outlinegrey.full.medium"
                );

                await timeSeriesBtn.click();

                await sleep(weightedDelay, logger, "time series button click");

                const closeBtn = await page.$("a.btn_layer_close");
                // scroll to bottom
                for (let i = 0; i < SCROLL_COUNT + scroll_count_offset; i++) {
                  if (!(productId in this.timeSeriesData)) {
                    weightedDelay += API_CALL_DELAY * retry;
                    logger.error(
                      `🚫 [${hrefCounter + 1}/${
                        hrefsLimited.length
                      }] 상품 정보 수집 실패: [${brand}]${
                        newProductMetaData.name
                      }(${newProductMetaData.product_id})`
                    );
                    if (closeBtn && closeBtn.click) {
                      await closeBtn.click();
                    }
                    return;
                  }

                  await sleep(weightedDelay);

                  if (getFlag()) {
                    // weightedDelay += API_CALL_DELAY * retry;
                  } else {
                    weightedDelay = API_CALL_DELAY;
                  }

                  logger.log(
                    `🚀 [${i + 1}/${
                      SCROLL_COUNT + scroll_count_offset
                    }] 스크롤 중...`
                  );
                  // logger.progress(
                  //   SCROLL_COUNT + scroll_count_offset,
                  //   i + 1,
                  //   `[${brand}]${newProductMetaData.name}(${newProductMetaData.product_id})`
                  // );

                  await page.evaluate(() => {
                    const scrollable = document.querySelector(".price_body");
                    if (!scrollable) return;
                    scrollable.scrollTop = scrollable.scrollHeight;
                  });

                  await sleep(SCROLL_DELAY);
                }
                successScrape = true;
              };

              for (let i = 0; i < retryCount; i++) {
                await scrollProductHistory(i + 1);

                if (successScrape) {
                  break;
                }

                await sleep(weightedDelay, logger, "retry delay");
              }

              if (successScrape) {
                // saveData(this.timeSeriesData[productId], productId);

                logger.log(
                  `📦 [${hrefCounter + 1}/${
                    hrefsLimited.length
                  }] 상품 정보 수집 완료: [${brand}]${
                    newProductMetaData.name
                  }(${newProductMetaData.product_id})`
                );
                logger.log(
                  `📦 [${brand}]${newProductMetaData.name}(${newProductMetaData.product_id}): $${this.timeSeriesData[productId].length} 건`
                );
              } else {
                logger.error(
                  `🚫 [${hrefCounter + 1}/${
                    hrefsLimited.length
                  }] 상품 정보 수집 실패: [${brand}]${
                    newProductMetaData.name
                  }(${newProductMetaData.product_id})`
                );
              }
              const scrapeEndTime = new Date().getTime();
              logger.log(`🕒 소요 시간: ${scrapeEndTime - scrapeStartTime}ms`);
              // logger.progress(hrefCounter + 1, hrefsLimited.length, brand);

              scrapeTimerList.push(scrapeEndTime - scrapeStartTime);
            }
          }
        }
      }

      await browser.close();

      this.report(scrapeTimerList);
    }
  }

  async test() {
    logger.init();

    /** @type {Record<string, TimeSeriesData[]>} */
    const data = {
      0: [
        {
          product_id: 0,
          price: 1000,
          option: "100",
          date_created: "2024-01-01T00:00:00Z",
          is_immediate_delivery_item: true,
        },
        {
          product_id: 0,
          price: 3000,
          option: "200",
          date_created: "2024-01-01T00:00:01Z",
          is_immediate_delivery_item: true,
        },
      ],
      10: [
        {
          product_id: 10,
          price: 2000,
          option: "100",
          date_created: "2024-01-01T00:00:00Z",
          is_immediate_delivery_item: true,
        },
        {
          product_id: 10,
          price: 4000,
          option: "200",
          date_created: "2024-01-01T00:00:01Z",
          is_immediate_delivery_item: true,
        },
      ],
    };

    for (const [key, value] of Object.entries(data)) {
      saveData(value, key);
      logger.log(`📦 ${key} 저장`);
      console.log(key, value);
    }

    logger.close();
  }
}

const scraper = new Scraper().instance;

export default scraper;
