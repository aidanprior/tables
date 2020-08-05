open System
open System.IO

type Name = {First:string; Last:string}
type Camper = {Name:Name; Rank:int}
type Counselor = {Name:Name; TableNo:int}
type CounselorTable = {Counselors:Counselor List; AideSlots:int; Aides:Name list}
type PrintTable = {TableNo:int; Camper:Camper; Campers:Camper list; Aides:Name list}
type Table = {Unfilled: CounselorTable; Campers:Camper list; CamperSlots:int; TotalRank:int}

let emptyName = {First="";Last=""}

let tableMax = 10
let mutable numTables = 21
let rand = Random DateTime.Now.Millisecond

// compile to single exe file:
// dotnet publish -r win-x86 -c Release /p:PublishSingleFile=true /p:PublishTrimmed=true

// WRAPPERS:

let trim (str: string) = str.Trim ()

let prepend lst v = v :: lst

let mapToIndexTuples = List.mapi (fun i elm -> (i, elm))

// GETTER WRAPPERS:

let getCamper printTable = printTable.Camper

let getCamperName (camper: Camper) = camper.Name 

let getCounselorName counselor = counselor.Name

let getTableNo table = table.Unfilled.Counselors.Head.TableNo

let getCounselors cTable = cTable.Counselors

let getAides (cTable: CounselorTable) = cTable.Aides

// UBIQUITOUS HELPERS:

let fullName {First=first; Last=last} = first + " " + last

let commaFullName {First=first; Last=last} = last + ", " + first

let allTableNames table = 
    List.map (fun c -> c.Name) table.Unfilled.Counselors @ table.Unfilled.Aides @ List.map (fun (c: Camper) -> c.Name) table.Campers 

// CONVERTING:

let convertFromCounselorTable counselorTable = 
    let spacesTaken = (List.length counselorTable.Counselors) + (List.length counselorTable.Aides)
    {
        Unfilled= counselorTable
        Campers= []
        CamperSlots= tableMax - spacesTaken
        TotalRank= 0
    }

let convertToPrintTable table = 
    {
        TableNo = table.Unfilled.Counselors.Head.TableNo
        Camper = table.Campers.Head
        Campers= table.Campers.Tail
        Aides= table.Unfilled.Aides
    }

let convertAllCounselorTables cTables = cTables |> List.map convertFromCounselorTable

let convertAllToPrintTables tables = tables |> List.map convertToPrintTable

// CONFLICTS GENERATION:

let isBasicConflict n1 n2 = n1.Last = n2.Last && n1.First <> n2.First

let hasConflict conflicts table name = 
    let hasTableNames set = 
        set 
        |> Set.filter (fun n -> 
                List.contains n (allTableNames table)
            ) 
        |> Set.isEmpty 
        |> not
    let setsWithName = Set.filter (fun nameSet -> Set.contains name nameSet) conflicts
    match Set.isEmpty setsWithName with
    | true -> false
    | false -> 
        setsWithName |> Set.filter hasTableNames |> Set.isEmpty |> not

let createConflictsForName names (conflicts: Set<Set<Name>>) name =
    let nameList = names |> List.filter (isBasicConflict name) |> Set.ofList
    match Set.count nameList with
        | 0 -> conflicts
        | _ -> name |> nameList.Add |> conflicts.Add

let generateConflicts names = names |> List.fold (createConflictsForName names) Set.empty

// SEEDING:

let sectionalize (lst: list<'a>) i = (lst.[0..i-1], lst.[i], lst.[i+1..lst.Length])

let shuffleList a = 
    let swap (b: _[]) x y =
        let tmp = b.[x]
        b.[x] <- b.[y]
        b.[y] <- tmp
    let arry = a |> Array.ofList
    Array.iteri (fun i _ -> swap arry i (rand.Next(i, Array.length arry))) arry
    arry |> List.ofArray

let matchNoConflict returnOp conflicts name table = 
    match hasConflict conflicts table name with
    | true -> 
        printfn "Conflict with %s at Table %i" (fullName name) (getTableNo table + 1)
        None
    | false -> returnOp

let tryTableWithCamper conflicts (camper: Camper) table  = 
    let campers = camper::table.Campers
    let op = 
        match table.CamperSlots with
        | slots when slots <= 0 -> 
            printfn "Table %i out of room for Campers" (getTableNo table + 1)
            None
        | slots -> 
            Some {
                Unfilled= table.Unfilled
                Campers= campers
                CamperSlots= slots - 1
                TotalRank = campers |> List.sumBy (fun cp -> cp.Rank)
            }
    
    matchNoConflict op conflicts camper.Name table
        

let tryTableWithAide conflicts aide counselorTable =
    let op =
        match counselorTable.AideSlots with
        | 0 -> 
            printfn "Table %i out of room for Aides" (counselorTable.Counselors.Head.TableNo + 1) 
            None
        | slots ->
            Some {
                Counselors= counselorTable.Counselors
                Aides= aide::counselorTable.Aides
                AideSlots= slots - 1
            }
    
    matchNoConflict op conflicts aide (convertFromCounselorTable counselorTable)

let getLowestCombinedRank dontWork campers tables = 
    let notInDontWork camper (i, _) = dontWork |> List.contains (i, camper) |> not

    let camperMin camper = 
        tables 
        |> mapToIndexTuples
        |> shuffleList 
        |> List.filter (notInDontWork camper)
        |> List.map (fun (i, t) -> (i, t.TotalRank + camper.Rank)) 
        |> List.minBy (fun (_, r) -> r)
    
    let camperToThreeTuple ci camper = 
        let (i, r) = camperMin camper
        (ci, i, r)
    
    campers 
    |> List.mapi camperToThreeTuple
    |> List.minBy (fun (_, _, r) -> r)

let seedAllCampers conflicts campers tables =
    let rec seedCamper dontWork conflicts campers2 tables =
        match campers2 with
        | [] -> 
            printfn "Finished Seeding Campers"
            tables
        | campers3 -> 
            let (cIndex, tIndex, _) = getLowestCombinedRank dontWork campers3 tables
            let camper = campers3.[cIndex]

            let (dw, newTables, newCampers) = 
                match tryTableWithCamper conflicts camper tables.[tIndex] with
                | None -> 
                    ((tIndex, camper)::dontWork, tables, campers3)
                | Some table ->
                    printfn "\t%s -> %i" (fullName camper.Name) (tIndex+1)

                    let (tfront, _, tback) = sectionalize tables tIndex
                    let (cfront, _, cback) = sectionalize campers3 cIndex
                    (dontWork, tfront @ [table] @ tback, cfront @ cback)
        
            seedCamper dw conflicts newCampers newTables

    seedCamper [] conflicts campers tables

let seedAides conflicts aides counselorTables =
    let rec seedAide conflicts aides2 (cTables: CounselorTable list) =
        match aides2 with
        | [] -> 
            printfn "Finished Seeding Aides"
            cTables
        | aides3 -> 
            let aIndex = rand.Next(aides3.Length)
            let ctIndex = rand.Next(cTables.Length)
            let randAide = aides3.[aIndex]
            let randCTable = cTables.[ctIndex]

            let (newAides, newCTables) = 
                match tryTableWithAide conflicts randAide randCTable with
                | None -> 
                    (aides3, cTables)
                | Some cTable ->
                    printfn "\t%s -> %i" (fullName randAide) (ctIndex+1)

                    let (ctfront, _, ctback) = sectionalize cTables ctIndex
                    let (afront, _, aback) = sectionalize aides3 aIndex
                    (afront @ aback, ctfront @ [cTable] @ ctback)
        
            seedAide conflicts newAides newCTables

    seedAide conflicts aides counselorTables


// PARSING:

let parseName (str: string) = 
    let matchWith = str.Split " " |> Seq.toList
    match matchWith with
    | f::rest -> {First=f; Last=String.Join (" ", rest)}
    | [] -> emptyName

let parseCamper (rank, line) = {Name=parseName line; Rank=rank}

let parseCommaSeperatedNames (line: string) = line.Split '\t' |> Seq.toList |> List.map (trim >> parseName)

let parseOutAides names =
    let containsCount v lst =
        let wOut = lst |> List.filter (fun x -> x=v) |> List.length
        List.length lst - wOut
    (
    containsCount {First="Aide"; Last=""} names,
    names |> List.filter (fun n -> n.First <> "Aide")
    )

let parseCounselorTable i line = 
    let (aideSlots, counselors) = line |> parseCommaSeperatedNames |> parseOutAides 
    let counselors = counselors |> List.map (fun n -> {Name=n; TableNo=i})
    {Counselors= counselors; AideSlots=aideSlots; Aides=[]}

let parseConflictSet line = line |> parseCommaSeperatedNames |> Set.ofList

// LOADING:

let readlines (filename: string) =
    use stream = new StreamReader(filename)
        
    let rec processLine line lst =
        match line with
        | null -> lst
        | (s: string) -> s |> trim |> prepend lst |> processLine (stream.ReadLine ())

    processLine (stream.ReadLine()) []

let loadCampers filename = 
    let lineNumberToRank i = (float i)/ (float numTables) |> int |> (+) 1
    readlines filename 
    |> List.mapi (fun i line -> (lineNumberToRank i, line) ) 
    |> List.map parseCamper

let loadCounselorTables filename =  
    let lines = readlines filename 
    numTables <- List.length lines
    lines |> List.rev |> List.mapi parseCounselorTable

let loadConflicts filename = readlines filename |> List.map parseConflictSet |> Set.ofList

let loadAides filename = readlines filename |> List.map parseName

// FORMATTING:

let rowListJoin (strList: string list) = String.Join ("\t", strList)

let formatConflictSet cSet = cSet |> Set.toList |> List.map fullName |> rowListJoin

let cellListJoin (strList: string list) = String.Join (", ", strList)

let createTableHeader printTable = "Table " + string (printTable.TableNo + 1)

// Old Table Format
// let formatTable table =
//     let counselorNameStrings = table.Unfilled.Counselors |> List.map (fun cs -> fullName cs.Name) |> cellListJoin
//     let aideNameStrings = table.Aides |> List.map fullName |> cellListJoin
//     let camperNameStrings = table.Campers |> List.rev |> List.map (fun cp -> fullName cp.Name) |> cellListJoin 
//     rowListJoin [string (table.Unfilled.Counselors.Head.TableNo+1); counselorNameStrings; aideNameStrings; camperNameStrings]

// WRITING:

let writeConflicts (filename: string) conflicts = 
    use stream = new StreamWriter(filename)
    let writeFormattedConflictSet = formatConflictSet >> stream.WriteLine
    conflicts |> Set.iter writeFormattedConflictSet

let pullOffCamperHead (printTable: PrintTable) = 
    match printTable.Campers with
    | [] -> None
    | [camper] -> 
        Some {
            TableNo = printTable.TableNo
            Camper = camper
            Campers= []
            Aides= printTable.Aides
        }
    | camper::rest -> 
        Some {
            TableNo = printTable.TableNo
            Camper = camper
            Campers= rest
            Aides= printTable.Aides
        }

let writeTables weekNumber printTables = 
    use stream = new StreamWriter (sprintf "Tables-Week%i.tsv" weekNumber)    
    let rec writeLine pTables =
        match pTables with
        | [] -> ()
        | _ ->
            pTables |> List.map (getCamper >> getCamperName >> fullName) |> rowListJoin |> stream.WriteLine
            writeLine (pTables |> List.choose pullOffCamperHead)
    
    printTables |> List.map createTableHeader |> rowListJoin |> stream.WriteLine
    writeLine printTables

let mapToNameTableNoList pTable =
    let tableNo = pTable.TableNo
    let camperNameStrs = pTable.Camper::pTable.Campers |> List.map (fun cp -> commaFullName cp.Name)
    let aideStrs = pTable.Aides |> List.map commaFullName
    camperNameStrs @ aideStrs |> List.map (fun str -> [str; string (tableNo + 1)])

let writeLookup weekNumber printTables = 
    use stream = new StreamWriter (sprintf "Lookup-Week%i.tsv" weekNumber)
    stream.WriteLine "Name:\tTable:" //Write Header
    printTables 
    |> List.collect mapToNameTableNoList
    |> List.sortBy (fun lst -> lst.Head)
    |> List.map rowListJoin
    |> List.iter stream.WriteLine
    
// MAIN STUFF:

let tryLoad (f: string -> 'a) filename : 'a option = 
    try
        Some (f filename)
    with
    | :? FileNotFoundException -> 
        printfn "Can't Find '%s' file" filename
        None

let exitProgram () =
    printfn "Press ENTER to exit"
    Console.ReadLine () |> exit 1 
    ()

let run (args: string list) =
    // printfn "%A" args 
    let parsedArgs = 
        match args.Head.EndsWith("main.fs") with
        | true -> args.Tail
        | false -> args
     
    let argExplainString = "Required Positional Arguments: (start week) (end week)"
    let (startWeek, endWeek) =
        match parsedArgs.Length with
        | 0 | 1  -> 
            printfn "%s" argExplainString |> exitProgram 
            (-1,-1)

        | 2 -> (int parsedArgs.[0], int parsedArgs.[1])
        | _ -> 
            printfn "%s" ("Too many arguments!!\n" + argExplainString) |> exitProgram
            (-1, -1)

    let campersFilename = "Camper List.tsv"
    let conflictsFilename = "Conflicts.tsv"
    let aidesFilename = "Aides.tsv"
    let counselorTableFilename = "Counselor Tables.tsv"

    let campersOption = tryLoad loadCampers campersFilename
    let aidesOption = tryLoad loadAides aidesFilename
    let tablesOption = tryLoad loadCounselorTables counselorTableFilename

    // Exit if any of the Files Couldn't be loaded
    match campersOption with
    | None -> exitProgram ()
    | Some campers ->
        match aidesOption with
        | None -> exitProgram ()
        | Some aides ->
            match tablesOption with
            | None -> exitProgram ()
            | Some cTables ->

                match tryLoad loadConflicts conflictsFilename with
                | None -> 
                    let names =  
                        cTables 
                        |> List.collect getCounselors 
                        |> List.map getCounselorName 
                        |> (@) (List.map getCamperName campers) 
                        |> (@) aides
                    printfn "Generating Conflicts instead..."
                    writeConflicts conflictsFilename (generateConflicts names)
                    printfn "Make any necessary changes to the file and re-run"
                    exitProgram ()
                
                | Some conflicts ->
                    // seed the tables and write it to a tsv
                    let seedThenWriteWeek weekNumber= 
                        printfn "Seeding Week %i" weekNumber
                        let pTables = 
                            cTables 
                            |> seedAides conflicts aides
                            |> convertAllCounselorTables
                            |> seedAllCampers conflicts campers
                            |> convertAllToPrintTables

                        pTables |> writeTables weekNumber
                        pTables |> writeLookup weekNumber

                    [startWeek..endWeek] |> List.iter seedThenWriteWeek


[<EntryPoint>]
let main argv =
    run (List.ofArray argv)
    0