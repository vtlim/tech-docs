# Linear flow of steps

https://docs.imply.io/polaris/ingestion-guide-event-hubs

```mermaid
flowchart LR
    id1(Get details\nfrom Azure):::classLinkFocus
    id2(Set up\nauthentication in Azure):::classLinkFocus
    id3(Create a\nKafka connection):::classLinkNonfocus
    id4(Start an\ningestion job):::classLinkNonfocus
    id1 --> id2 --> id3 --> id4
    click id1 "#get-details-from-azure"
    click id2 "#set-up-authentication-in-azure"
    click id3 "#create-a-kafka-connection"
    click id4 "#start-an-ingestion-job"
    classDef classLinkNonfocus fill:#fff2ccff, stroke:#fff2ccff, stroke-width:4, color:#3578e5
    classDef classLinkFocus fill:#ffffff, stroke:#ffd966, stroke-width:2px, color:#3578e5
```

# Linear flow with different environments

https://docs.imply.io/polaris/ingestion-overview/

```mermaid
flowchart LR
  id2("Create a table\n(optional)"):::classLink
  id3(Start an\ningestion job):::classLink
  id4(Upload files):::classLink
  id5(Create a\nconnection):::classLink
  id6(Identify an\nexisting table):::classLink

  subgraph A["Specify a data source"]
    direction TB
    id4
    id5
    id6
  end

classDef classLink fill:#ffffff, stroke:#892DFF, stroke-width:2px, color:#3578e5

A --> id2 --> id3

click id2 "#create-a-table"
click id3 "#start-an-ingestion-job"
click id4 "#specify-a-data-source"
click id5 "#specify-a-data-source"
click id6 "#specify-a-data-source"
```

# Relationship diagram

```mermaid
%%{init: { "flowchart": { "padding": 20 } } }%%
flowchart LR
    classDef hidden display: none;
    style ProductA fill:#edf5ff, stroke:#008adc, stroke-width:1.5px;
    style ProductB fill:#ffeecf, stroke:#ffaa0f, stroke-width:1.5px;
    subgraph ProductA["\n<font size=5>ProductA</font>"]
      id1("x"):::hidden
      id2("component\n<b>main</b>")
    end
    subgraph ProductB["\n<font size=5>ProductB</font>"]
      id3("x"):::hidden
      id4("component\n<b>main</b>")
      subgraph FP ["\nbig box\n<b><center>big name</b>"]
        id5("x"):::hidden
        id6("little box\n<b>little name</b>")
      end
      id7("search")
      id4--> |"<span style=background-color:#fff>&nbsp; relationship1 &nbsp;</span>"|id7
      id6--> |"<span style=background-color:#fff>&nbsp; relationship2 &nbsp;</span>"|id7
    end
    id2 --> id6
```
