require(XML)
require(stringr)
require(sendmailR)

dl_dir <- 'dl'
if(!file.exists('dl')) dir.create('dl')
str_remove_white <- function(x){str_replace_all(x,'[[:space:]]','')}

#########################
##
## PITCHFORK
##
#########################
get_pitchfork_reviews <- function(){

    url <- 'http://pitchfork.com'
    main <- file.path(dl_dir,'index.html')
    nvalues <- 5

    info <- list(
        name = 'Pitchfork',
        score = numeric(nvalues),
        album = character(nvalues),
        artist = character(nvalues),
        label = character(nvalues),
        year =  numeric(nvalues),
        nvalues = nvalues
    )

    download.file(url,main,quiet=F)
    oo <- htmlTreeParse(main,useInternalNodes = TRUE)
        # then spit is back out in a form R can read easily
    links <- unique(sapply(xpathApply(oo, "//div[@class='review-detail']/div/a",xmlAttrs),'['))[1:5]

    for(i in 1:5){
        this.html <- file.path(dl_dir,paste(i,'html',sep='.'))
        download.file(paste(url,links[i],sep=''),this.html,quiet=F)
        o <- htmlTreeParse(this.html,useInternalNodes = TRUE)
        #browser()
        info$artist[i] <- xpathApply(o, "//ul[@class='review-meta']/li/div/h1",xmlValue)[[1]]
        info$album[i] <- xpathApply(o, "//ul[@class='review-meta']/li/div/h2",xmlValue)[[1]]
        xx <- str_split(xpathApply(o, "//ul[@class='review-meta']/li/div/h3",xmlValue)[[1]],';')[[1]]
        info$label[i] <- str_trim(xx[1])
        info$year[i] <- str_trim(xx[2])
        info$score[i] <- str_trim(xpathApply(o, "//div[@class='info']/span",xmlValue)[[1]])
    }

    return(info)
}

print_review_summary <- function(info,file){
    
    for(i in 1:info$nvalues){
        
        with(info,{
            cat(artist[i],'-',album[i],':',score[i],'\n',file=file)
            cat('\t',label[i],';',year[i],'\n\n',file=file)
        })
        
    }
    
}
         
info <- get_pitchfork_reviews()
print_review_summary(info,'whats-cool.txt')

from <- 'Cameron'
to <- "cameron.bracken@gmail.com"
subject <- "Pitchfork Summary"
body <- list(readLines('whats-cool.txt'))
sendmail(from, to, subject, body,
         control=list(smtpServer="smtp.webfaction.com"))

