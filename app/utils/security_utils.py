def mask_sensitive_data(data: dict) -> dict:
    """Mask sensitive information in the data"""
    masked_data = data.copy()
    sensitive_fields = [
        'Caller', 'From', 'Called', 'To', 'CallSid', 'AccountSid',
        'CallToken', 'CallerZip', 'CalledZip', 'FromZip', 'ToZip'
    ]
    
    for field in sensitive_fields:
        if field in masked_data:
            value = masked_data[field]
            if value:
                # Keep first 3 and last 3 characters, mask the rest
                if len(value) > 6:
                    masked_data[field] = value[:3] + '*' * (len(value) - 6) + value[-3:]
                else:
                    masked_data[field] = '*' * len(value)
    
    return masked_data 