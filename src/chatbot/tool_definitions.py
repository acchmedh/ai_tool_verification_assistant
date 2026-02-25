tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "Get today's current date in YYYY-MM-DD format.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_days_to_date",
            "description": "Add a number of days to a given date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_str": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to add",
                    },
                },
                "required": ["date_str", "days"],
            },
        },
    },
]