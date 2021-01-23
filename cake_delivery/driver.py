import time

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

from cake_delivery.config import cfg


class OrderBot:
    def __init__(self):
        options = None
        if cfg["SELENIUM"]["HEADLESS"]:
            options = Options()
            options.add_argument("--headless")
        self.driver = webdriver.Chrome(cfg["SELENIUM"]["CHROMEDRIVER_PATH"], options=options)

    def _go_to_order_page(self):
        self.driver.get(cfg["SELENIUM"]["ORDER_URL"])

    @staticmethod
    def _find_element_by_text(ele, text):
        return ele.find_element_by_xpath(f"//*[contains(text(), '{text}')]")

    def _set_delivery_address_and_time(self):
        # choose delivery option
        while True:
            try:
                self.driver.find_element_by_id("DeliveryModeDispatch").click()
                self.driver.find_element_by_id("addnewaddress").click()
                break
            except (exceptions.ElementClickInterceptedException, exceptions.ElementNotInteractableException):
                time.sleep(0.5)

        # fill in delivery address
        while True:
            try:
                street_ele = self.driver.find_element_by_id("streetaddress")
                street_ele.clear()
                street_ele.send_keys(cfg["DELIVERY"]["STREET"])
                building_ele = self.driver.find_element_by_id("building")
                building_ele.clear()
                building_ele.send_keys(cfg["DELIVERY"]["APT"])
                city_ele = self.driver.find_element_by_id("city")
                city_ele.clear()
                city_ele.send_keys(cfg["DELIVERY"]["CITY"])
                zipcode_ele = self.driver.find_element_by_id("zipcode")
                zipcode_ele.clear()
                zipcode_ele.send_keys(cfg["DELIVERY"]["ZIPCODE"])
                instruction_ele = self.driver.find_element_by_id("instructions")
                instruction_ele.clear()
                instruction_ele.send_keys(cfg["DELIVERY"]["INSTRUCTION"])
                if cfg["DELIVERY"]["CONTACTLESS"]:
                    checkbox_ele = self.driver.find_element_by_id("contactlessCheckbox")
                    checkbox_ele.click()
                save_ele = self._find_element_by_text(self.driver, "Save Address")
                save_ele.click()
                break
            except exceptions.NoSuchElementException:
                time.sleep(0.5)

        # fill in delivery time
        while True:
            try:
                date_ele = self.driver.find_element_by_id("DatePicker")
                date_ele.clear()
                date_ele.send_keys(
                    f"{cfg['DELIVERY']['MONTH']}/"
                    f"{cfg['DELIVERY']['DAY']}/"
                    f"{cfg['DELIVERY']['YEAR']}"
                )
                time.sleep(0.5)  # wait for possible alerts to pop up
                alerts = self.driver.find_elements_by_id("ConfirmAlert")
                if len(alerts) > 1:
                    alerts[-1].click()
                select_ele = Select(self.driver.find_element_by_id("selTimeWanted"))
                select_ele.select_by_value(cfg["DELIVERY"]["TIME"])
                self.driver.find_element_by_id("selectTimeWanted").click()
                time.sleep(2)  # wait for time confirmation
                break
            except exceptions.NoSuchElementException:
                time.sleep(0.5)

        self.driver.find_element_by_id("proceedButton").click()

        # wait for possible suggestion boxes to pop up
        time.sleep(1)
        try:
            self.driver.find_element_by_id("CancelUpsell").click()
        except exceptions.NoSuchElementException:
            pass

    def _add_items_to_cart(self):
        for category_name, product_name, qty in cfg["SHOPPING_LIST"]:
            # go to category
            while True:
                try:
                    self._find_element_by_text(
                        self.driver.find_element_by_id("CategoryList"),
                        category_name
                    ).click()
                    break
                except exceptions.ElementNotInteractableException:
                    time.sleep(0.5)

            # find product
            while True:
                try:
                    self._find_element_by_text(
                        self.driver.find_element_by_id("ProductList"),
                        product_name
                    ).click()
                    break
                except exceptions.ElementNotInteractableException:
                    time.sleep(0.5)

            # put quantity
            while True:
                try:
                    qty_ele = self.driver.find_element_by_id("qty")
                    qty_ele.clear()
                    qty_ele.send_keys(qty)
                    break
                except exceptions.NoSuchElementException:
                    time.sleep(0.5)

            # add to cart
            while True:
                try:
                    self.driver.find_element_by_id("AddProductToBasket").click()
                    break
                except exceptions.ElementNotInteractableException:
                    time.sleep(0.5)

    def _proceed_to_checkout(self):
        self.driver.find_element_by_id("UserType_Guest").click()
        firstname_ele = self.driver.find_element_by_id("firstname")
        firstname_ele.clear()
        firstname_ele.send_keys(cfg["PAYMENT"]["FIRSTNAME"])
        lastname_ele = self.driver.find_element_by_id("lastname")
        lastname_ele.clear()
        lastname_ele.send_keys(cfg["PAYMENT"]["LASTNAME"])
        email_ele = self.driver.find_element_by_id("emailaddress")
        email_ele.clear()
        email_ele.send_keys(cfg["PAYMENT"]["EMAIL"])
        phone_ele = self.driver.find_element_by_id("txtContactNumber")
        phone_ele.clear()
        phone_ele.send_keys(cfg["PAYMENT"]["PHONE"])
        card_ele = self.driver.find_element_by_id("txtNumber")
        card_ele.clear()
        card_ele.send_keys(cfg["PAYMENT"]["CARD_NUMBER"])
        cvv_ele = self.driver.find_element_by_id("txtCvv")
        month_ele = Select(self.driver.find_element_by_id("selExpiryMonth"))
        month_ele.select_by_visible_text(cfg["PAYMENT"]["EXPIRATION_MONTH"])
        year_ele = Select(self.driver.find_element_by_id("selExpiryYear"))
        year_ele.select_by_visible_text(cfg["PAYMENT"]["EXPIRATION_YEAR"])
        cvv_ele.clear()
        cvv_ele.send_keys(cfg["PAYMENT"]["SECURITY_CODE"])
        zipcode_ele = self.driver.find_element_by_id("txtZip")
        zipcode_ele.clear()
        zipcode_ele.send_keys(cfg["PAYMENT"]["ZIPCODE"])
        self.driver.find_element_by_id("MvcCheckoutPlaceOrder").click()
        # wait for confirmation
        while True:
            try:
                self.driver.find_element_by_id("ThankYouContainer")
                break
            except exceptions.NoSuchElementException:
                time.sleep(0.5)
        print(f"Order Placed! Please check confirmation email in {cfg['PAYMENT']['EMAIL']}.")

    def start(self):
        self._go_to_order_page()
        self._add_items_to_cart()
        self._set_delivery_address_and_time()
        self._proceed_to_checkout()

    def __del__(self):
        self.driver.close()
