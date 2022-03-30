// formatStr("{0} is dead, but {1} is alive! {0} {2}", "ASP", "ASP.NET") 
// OUTPUT: ASP is dead, but ASP.NET is alive! ASP {2}

const formatStrFunction = function (str, ...args) {
    return str.replace(/{(\d+)}/g, function(match, number) { 
      return typeof args[number] != 'undefined'
        ? args[number]
        : match
      ;
    });
  };

const getNote = (note) => {
      if (note.length > 150 )
        return note.substring(0, 150) + " ..."
      else 
        return note
    }

export default (context, inject) =>
  {
    inject('formatStr', formatStrFunction)
    inject('getNote', getNote)
  }

