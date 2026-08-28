import xml.etree.ElementTree as ET
import csv
import json
import logging
import os
import tempfile
from typing import Dict, Any

def load_mapping(mapping_path: str) -> Dict[str, Any]:
    with open(mapping_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def strip_ns(tag: str) -> str:
    return tag.split('}', 1)[-1]

def process_value_node(element: ET.Element, culture: str) -> str:
    """Extracts the best text from multi-lingual <value> or <text> children."""
    values = []
    for child in element:
        if strip_ns(child.tag) in ('value', 'text') and child.text and child.text.strip():
            lang = child.get("lang") or child.get("{http://www.w3.org/XML/1998/namespace}lang")
            values.append({"val": child.text.strip(), "lang": lang})
    
    if values:
        # Match exact culture first (e.g. 'en')
        for v in values:
            if v["lang"] and v["lang"].startswith(culture):
                return v["val"]
        # Fallback to the first available translation
        return values[0]["val"]
        
    if element.text and element.text.strip():
        return element.text.strip()
    return None

def extract_elements(element: ET.Element, culture: str, record_data: Dict[str, list] = None) -> Dict[str, list]:
    if record_data is None:
        record_data = {}
        priref = element.get("priref")
        if priref:
            record_data["priref"] = [priref]
            
    clean_tag = strip_ns(element.tag)
    
    # If this node contains <value> or <text> children (WebAPI multilingual), process as a single unit
    has_value_children = any(strip_ns(c.tag) in ('value', 'text') for c in element)
    
    if has_value_children:
        val = process_value_node(element, culture)
        if val:
            record_data.setdefault(clean_tag, []).append(val)
    else:
        if element.text and element.text.strip() and clean_tag not in ('value', 'text'):
            val = element.text.strip()
            # Deduplicate ONLY priref to prevent 10|10 if it exists as both attribute and child
            if clean_tag == "priref":
                if val not in record_data.get("priref", []):
                    record_data.setdefault(clean_tag, []).append(val)
            else:
                record_data.setdefault(clean_tag, []).append(val)
        
        for child in element:
            extract_elements(child, culture, record_data)
            
    return record_data

def parse_adlib_record(record_elem: ET.Element, mapping: Dict[str, Any], repository: str, culture: str) -> Dict[str, str]:
    out_row = {}
    record_data = extract_elements(record_elem, culture)

    for atom_col, rules in mapping.items():
        vals = []
        for source_tag in rules.get("source_tags", []):
            if source_tag in record_data:
                vals.extend(record_data[source_tag])
                if not rules.get("join"): break
        
        if not vals:
            val = rules.get("fallback", "")
        else:
            join_char = rules.get("join_char", "|")
            val = join_char.join(vals)
            
        out_row[atom_col] = val

    if repository: out_row['repository'] = repository
    if culture: out_row['culture'] = culture
    
    # Enforce strictly parallel arrays for AtoM events, padded with literal "NULL"
    actor_count = len(out_row["eventActors"].split("|")) if out_row.get("eventActors") else 0
    sdate_count = len(out_row["eventStartDates"].split("|")) if out_row.get("eventStartDates") else 0
    edate_count = len(out_row["eventEndDates"].split("|")) if out_row.get("eventEndDates") else 0
    max_events = max(actor_count, sdate_count, edate_count)

    if max_events > 0:
        actors = out_row.get("eventActors", "").split("|") if out_row.get("eventActors") else []
        out_row["eventActors"] = "|".join(actors + ["NULL"] * (max_events - len(actors)))
        
        base_type = mapping.get("eventTypes", {}).get("fallback", "Creation")
        types = out_row.get("eventTypes", "").split("|") if out_row.get("eventTypes") else []
        types = [t if t else base_type for t in types]
        out_row["eventTypes"] = "|".join(types + [base_type] * (max_events - len(types)))
        
        sdates = out_row.get("eventStartDates", "").split("|") if out_row.get("eventStartDates") else []
        out_row["eventStartDates"] = "|".join(sdates + ["NULL"] * (max_events - len(sdates)))
            
        edates = out_row.get("eventEndDates", "").split("|") if out_row.get("eventEndDates") else []
        out_row["eventEndDates"] = "|".join(edates + ["NULL"] * (max_events - len(edates)))
    else:
        if "eventTypes" in out_row:
            out_row["eventTypes"] = ""

    return out_row

def convert_adlib_to_atom(input_xml: str, output_csv: str, mapping_path: str, repository: str, culture: str):
    mapping = load_mapping(mapping_path)
    context = ET.iterparse(input_xml, events=("end",))
    records_processed = 0
    headers = list(mapping.keys())
    for h in ['repository', 'culture']:
        if h not in headers: headers.append(h)
        
    output_dir = os.path.dirname(os.path.abspath(output_csv))
    os.makedirs(output_dir, exist_ok=True)
    temp_fd, temp_path = tempfile.mkstemp(suffix=".csv", dir=output_dir, text=True)
    
    try:
        with os.fdopen(temp_fd, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
            for event, elem in context:
                if strip_ns(elem.tag) == 'record':
                    row = parse_adlib_record(elem, mapping, repository, culture)
                    if row.get("identifier") == "UNKNOWN" and row.get("legacyId"):
                        row["identifier"] = row["legacyId"]
                    writer.writerow(row)
                    records_processed += 1
                    elem.clear()
        
        if records_processed == 0:
            os.remove(temp_path)
            raise ValueError("No records found. Check XML format/namespaces.")
            
        os.replace(temp_path, output_csv)
        logging.info(f"Successfully converted {records_processed} Adlib records to {output_csv}.")
        return records_processed
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e
