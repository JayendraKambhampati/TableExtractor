import org.apache.pdfbox.pdmodel.PDDocument
import org.apache.pdfbox.text.PDFTextStripper
import technology.tabula.ObjectExtractor
import technology.tabula.extractors.SpreadsheetExtractionAlgorithm
import java.io.File


fun main(args: Array<String>) {

    try{
        val pathname = "schools.pdf"
        val pd = PDDocument.load(File(pathname))
        val totalPages = pd.numberOfPages
        println("Total Pages in Document: $totalPages")
        val oe = ObjectExtractor(pd)
        val sea = SpreadsheetExtractionAlgorithm()




        val stripper = PDFTextStripper()
        val count = pd.numberOfPages

        for(i in 1 .. count){
            val page = oe.extract(i)
            val table = sea.extract(page)
            var tables_count = 0
            //println("Table $i: \n")
            for (tables in table) {
                val rows = tables.rows
                for (i in rows.indices) {
                    val cells = rows[i]
                    for (j in cells.indices) {
                        //print(cells[j].getText() + "  |  ")
                    }
                    //println()
                }
                tables_count++
            }
            println("\nNumber of tables in page $i are $tables_count")
            println("\n\n\n")
        }
    }catch(ex:Exception){
        println(ex.stackTrace)
        println("Error occured")
    }
}
