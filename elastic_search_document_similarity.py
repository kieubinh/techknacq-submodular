from lxml import etree
import elasticsearch
import urllib
import math
import csv
import time


html_parser = etree.HTMLParser(remove_comments=True)


# Utils
def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])
    
    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    
    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator

def get_tv_dict(tvjson):
    return dict([ (k, v['term_freq'])  
                  for k,v in tvjson\
                  .get('term_vectors')\
                  .get('page_text')\
                  .get('terms')\
                  .iteritems()])



def create_or_clear_index(_obj):
    index_name = _obj
    es = elasticsearch.Elasticsearch()
    
    # Delete index if already found one
    try:
        es.indices.delete(index = index_name)
    except elasticsearch.NotFoundError:
        pass
        
    # Setup fresh index and mapping
    es.indices.create(index = index_name,
                      body = {
                          "mappings": {
                              "page": {
                                  "_source": { "enabled": True },
                                  "properties": {
                                      "url": {
                                          "type": "string"
                                      },
                                      "page_text": {
                                          "type": "string",
                                          "term_vector": "yes"
                                      },
                                      "title": {
                                          "type": "string",
                                          "term_vector": "yes"
                                      }
                                  }
                              }
                          }})


def generate_mlt_report(index_name, max_link_id):
    
    fd = open("output.csv",'w')
    out_csv = csv.writer(fd)
    
    es = elasticsearch.Elasticsearch()
    
    def collect_mlt_scores(doc_id):
        try:
            d = es.get(index=index_name,
                       doc_type="page", id=doc_id)
            
            dsrc = d.get("_source")
            url = dsrc.get("url")
            title = dsrc.get("title")
            
            mlts = es.mlt(index=index_name, doc_type="page",
                          id=doc_id, mlt_fields="page_text", 
                          search_size=2,min_term_freq=1,min_doc_freq=1)
            hits = mlts.get('hits').get('hits')
            print(index_name, doc_id,mlts)
            tvjson = es.termvector(index=index_name, doc_type="page",
                                   id=doc_id)
            #print tvjson
            tv1 = get_tv_dict(tvjson)
            wc = sum(tv1.values())
            r = [doc_id, title.encode('ascii', 'ignore'), url, wc]
            tmp_li = []
            for h in hits:
                tmp_tvjson = es.termvector(index=index_name,
                                           doc_type="page",
                                           id=h.get('_id'))
                tmp_tv = get_tv_dict(tmp_tvjson)
                                                        
                
                
                
                tmp_li.extend([[h.get('_id'), h.get('_score'),
                          get_cosine(tv1, tmp_tv) * 100,
                          h.get('_source').get('title').encode('ascii', 'ignore'),
                          h.get('_source').get('url'), sum(tmp_tv.values())]])
                #print tmp_li
            tmp_li = sorted(tmp_li,key=lambda a:a[2],reverse=True)  
            tmp_li2 = []
            
            for do in tmp_li:
                tmp_li2 = tmp_li2+do
            
            r = r+tmp_li2
            #print r  
            out_csv.writerow(r)
            fd.flush()
        except Exception as e:
            print(e)
    
    map(collect_mlt_scores, range(max_link_id))
    fd.close()
            

if __name__=='__main__':
    es = elasticsearch.Elasticsearch()

    if True:
        index_name = 'kpsindex'
        create_or_clear_index(index_name)

        num_urls = 0
        links = None
        doc_count = None



        _tlinks = open('urls_file.txt').read().strip().split('\n')
        doc_count = len(_tlinks)
        links = enumerate(_tlinks)



        def crawl_link_to_index(inp):
            idx, link = inp
            print(idx, link)
            try:
                print(link)
                response= urllib.urlopen(link)

                while response.getcode()==502:
                    time.sleep(60)
                    response= urllib.urlopen(link)
                page_content = response.read()


                tree = etree.HTML(page_content, parser=html_parser)
                etree.strip_elements(tree, 'script')
                etree.strip_tags(tree, 'script')
                text_data = "\n".join(filter(lambda chunk: chunk != '',
                            [t.strip() for t in tree.itertext()]))

                page_title = tree.find(".//title").text

                es.index(index = index_name,
                         doc_type = "page",
                         id = idx,
                         body = {
                             "url": link,
                             "title": page_title,
                             "page_text": text_data
                         })
                print("-" * 10)
            except Exception as e:
                print(e)

        if links:
            map(crawl_link_to_index, links)
            print('Starting with generating mlt report')
            time.sleep(5)
            generate_mlt_report(index_name, doc_count)
        else:
            print("no links")



