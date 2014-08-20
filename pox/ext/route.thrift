struct Query
{
    1: required list<string> arguments
}

struct QueryReply
{
    1: required list<list<string>> result,
    2: optional string exception_code,
    3: optional string exception_message
}

service GetRouteEntry{
    QueryReply get(1:Query request)
}
