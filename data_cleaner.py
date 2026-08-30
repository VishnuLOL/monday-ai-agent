import pandas as pd
import re

class DataNormalizer:
    def clean_deals(self, raw_deals: list[dict]) -> tuple[pd.DataFrame, dict]:
        df = pd.DataFrame(raw_deals)
        flags = {"total_records": len(df), "missing_values": {}}
        
        if df.empty: return df, flags

        # 1. Normalize rel-key and categorical text
        if 'Deal Name' in df.columns:
            df['Deal Name'] = df['Deal Name'].astype(str).str.strip().str.title()
        
        if 'Owner code' in df.columns:
            # Fixes 'OWNER _003' vs 'OWNER_003'
            df['Owner code'] = df['Owner code'].astype(str).str.replace(' ', '').str.upper()
            
        for col in ['Deal Status', 'Deal Stage', 'Sector/service']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.title()

        # 2. Date formatting
        for date_col in ['Close Date (A)', 'Tentative Close Date', 'Created Date']:
            if date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col], format='mixed', errors='coerce')

        # 3. Numeric Coercion (Masked Deal value)
        if 'Masked Deal value' in df.columns:
            df['Masked Deal value'] = pd.to_numeric(df['Masked Deal value'], errors='coerce').fillna(0)

        flags["missing_values"] = df.isna().sum().to_dict()
        return df, flags

    def clean_work_orders(self, raw_wo: list[dict]) -> tuple[pd.DataFrame, dict]:
        df = pd.DataFrame(raw_wo)
        flags = {"total_records": len(df), "missing_values": {}}
        
        if df.empty: return df, flags

        # 1. Normalize rel-key to match Deals board
        if 'Deal name masked' in df.columns:
            df['Deal name masked'] = df['Deal name masked'].astype(str).str.strip().str.title()
            
        if 'Customer Name Code' in df.columns:
            df['Customer Name Code'] = df['Customer Name Code'].astype(str).str.replace(' ', '_').str.upper()

        for col in ['Execution Status', 'Sector', 'WO Status (billed)']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.title()

        # 2. Clean corrupted numeric fields (e.g. '5360 НА', '#VALUE!')
        numeric_cols = ['Amount in Rupees (Excl of GST) (Masked)', 'Quantity by Ops']
        for col in numeric_cols:
            if col in df.columns:
                # Strip everything except numbers and decimals
                df[col] = df[col].astype(str).apply(lambda x: re.sub(r'[^\d.]', '', x))
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 3. Date Formatting
        for date_col in ['Data Delivery Date', 'Date of PO/LOI', 'Probable Start Date', 'Probable End Date']:
            if date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col], format='mixed', errors='coerce')

        flags["missing_values"] = df.isna().sum().to_dict()
        return df, flags