import logging

from selectolax.parser import HTMLParser

from .models import (
    Organic,
    Adword,
    MapsSidebar,
    Serp,
)


def get_organic_results(tree):
    return_list = []
    results = tree.css("div.g")

    for result in results:
        result_dict = {}

        if display_path := result.css_first("cite.iUh30"):
            result_dict["display_path"] = display_path.text(separator=" ")

        if title := result.css_first("h3"):
            result_dict["title"] = title.text(deep=False, separator=" ")

        if url := result.css_first("a[href]"):
            result_dict["url"] = url.attributes.get("href")

        if description := result.css_first("div.IsZvec"):
            result_dict["description"] = description.text(separator=" ")

        # TODO: extract Reviews and Video

        try:
            return_list.append(Organic.parse_obj(result_dict))
        except Exception as e:
            logging.info(f"Error in parsing Organic result: {e}")

    return return_list


def get_adwords_results(tree):
    return_list = []
    results = tree.css("div.uEierd")

    for result in results:
        result_dict = {}
        if heading := result.css_first("div[role='heading']"):
            result_dict["title"] = heading.text()

        if description := result.css_first("div.yDYNvb"):
            result_dict["description"] = description.text()

        if url := result.css_first("span.Zu0yb"):
            result_dict["visual_url"] = url.text()

        try:
            return_list.append(Adword.parse_obj(result_dict))
        except Exception as e:
            logging.info("Error in parsing Adwords result")

    return return_list


def get_maps_sidebar(tree):
    know_p = tree.css_first("div.g.VjDLd")

    if not know_p:
        return

    return_dict = {}
    # get the title
    if title := know_p.css_first("h2[data-attrid='title']"):
        return_dict["title"] = title.text()

    # check if closed
    if "Tijdelijk gesloten" in know_p.html:
        return_dict["gesloten"] = "tijdelijk gesloten"
    if "Permanent gesloten" in know_p.html:
        return_dict["gesloten"] = "permanent gesloten"

    # get the company type
    unders = know_p.css("span.YhemCb")
    if unders:
        return_dict["company_type"] = unders[-1].text()

    # get the website
    if website := know_p.css_first("a.ab_button[href]"):
        if website.attributes.get("href") != "#":
            return_dict["website"] = website.attributes.get("href")

    # get the address
    adresses = know_p.css("div[data-local-attribute='d3adr']")
    for adr in adresses:
        if addr := adr.css_first("span.LrzXr"):
            return_dict["address"] = addr.text()

    # get the phone nr
    phones = know_p.css("div[data-local-attribute='d3ph']")
    for ph in phones:
        if phs := ph.css_first("span.LrzXr"):
            return_dict["phone"] = phs.text()

    # for restaurants
    # get checkmarks
    if checkmarks := know_p.css("li.A4D4f[aria-label]"):
        return_dict["checks"] = []
        for check in checkmarks:
            the_bool = bool(check.css_first("svg.GmYtSd"))
            return_dict["checks"].append((check.attributes.get("aria-label"), the_bool))

    if rest_reserveren := know_p.css_first(
        "div[data-attrid='kc:/local:table_reservations']"
    ):
        return_dict["restaurant_reserveren"] = []
        for ahref in rest_reserveren.css("a[href]"):
            return_dict["restaurant_reserveren"].append(
                {"title": ahref.text(strip=True), "url": ahref.attributes.get("href")}
            )

    if bestellen := know_p.css_first("div[data-attrid$='order_food']"):
        return_dict["bestellen"] = []
        bestel_list = bestellen.css("a[href]")
        for bst_a in bestel_list:
            return_dict["bestellen"].append(
                {"title": bst_a, "url": bst_a.attributes.get("href")}
            )

    if service_elem := know_p.css_first(
        "div[data-attrid='kc:/local:business_availability_modes']"
    ):
        service_elem.strip_tags(["span"])
        split_str = [item.strip() for item in service_elem.text().split("??") if item]
        return_dict["services"] = split_str

    if review_elem := know_p.css_first(
        "div[data-attrid='kc:/collection/knowledge_panels/local_reviewable:star_score']"
    ):
        grade = review_elem.css_first("span").text()
        grade = grade.replace(",", ".")
        nr_reviews_string = review_elem.css_first("a").text()
        nr_reviews = "".join([token for token in nr_reviews_string if token.isdigit()])
        return_dict["review"] = {"grade": float(grade), "nr_reviews": int(nr_reviews)}

    try:
        for a_href in know_p.css("a[href]"):
            if a_href.attributes.get(
                "href"
            ) and "/travel/hotels/entity/" in a_href.attributes.get("href"):
                split_path = a_href.attributes.get("href").split("/")
                hotel_path = "/".join(split_path[:5])
                return_dict["hotel_page"] = hotel_path
                break
    except Exception:
        pass

    try:
        return MapsSidebar.parse_obj(return_dict)
    except Exception as e:
        logging.info(f"Error parsing maps sidebar. {e}")


def get_related_queries(tree):
    rel_a = tree.css("a.k8XOCe")
    return [a.text(separator=" ") for a in rel_a]


def parse_html(html: str) -> Serp:
    tree = HTMLParser(html)

    organic_results = get_organic_results(tree)
    adwords_results = get_adwords_results(tree)
    maps_sidebar = get_maps_sidebar(tree)
    related = get_related_queries(tree)

    return {
        "organic_results": organic_results,
        "adwords_results": adwords_results,
        "maps_sidebar": maps_sidebar,
        "related": related,
    }
